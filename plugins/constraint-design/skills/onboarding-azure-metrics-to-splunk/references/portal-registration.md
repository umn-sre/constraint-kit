# Portal Registration Reference

Every field on the metrics portal's team forms, what the service actually
does with it, and how to fill it in. Field behavior here is taken from the
service's orchestrator and HEC formatter, not from the form labels — where
the two disagree, this document follows the code.

## Metric Subscription (platform metrics)

| Field | Required | What it must be |
|---|---|---|
| Azure Resource ID | yes | Full ARM resource ID of **one** resource |
| Metric Namespace | yes | e.g. `Microsoft.Compute/virtualMachines` |
| Metric Names | yes | Comma-separated, exactly as Azure spells them |
| Polling Interval (minutes) | no (default 5) | **Leave at 5** — see below |
| Splunk Source | no (default `azure:metric`) | Splunk `source` field |
| HEC Target | yes | Edge Processor, from SRE's dropdown |
| Target Index | yes | `test` or `prod` |
| Enabled | — | Unchecked stops collection immediately |

### Azure Resource ID

One resource per subscription record. This field takes a resource ID, not
a resource group — a resource-group scope in your Terraform grants access
to everything in the group, but you still register each resource
individually here.

```
/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Web/sites/my-app
```

The service derives Splunk dimensions by parsing this string:
`subscription_id`, `resource_group`, `resource_type`, `resource_name`.
The Splunk `host` field is set to the resource name. A malformed resource
ID produces empty dimensions rather than an error.

### Metric Namespace and Metric Names

Both are passed straight to Azure Monitor. Names must match Azure's
spelling exactly, including spaces and capitals — `Percentage CPU`, not
`percentage_cpu`. A wrong name yields no data and no obvious error.

To find the real names for a resource:

```bash
az monitor metrics list-definitions \
  --resource "<resource-id>" \
  --query "[].{name:name.value, unit:unit}" -o table
```

Metric names are split on commas and stripped, so
`Percentage CPU, Available Memory Bytes` is fine.

### Polling Interval — a lookback window, not a schedule

The function's timer is hard-coded to `0 */5 * * * *`. Every subscription
is evaluated every 5 minutes regardless of this value.

What this field actually sets is the **timespan of the Azure Monitor
query**. Setting 60 means: every 5 minutes, request the last 60 minutes.
The same points are re-sent about 12 times.

**Leave it at 5.** Raise it only for a metric Azure populates on a slower
cadence, and only knowing you're accepting duplicates. Lowering it below 5
leaves gaps between cycles.

### Aggregations you'll receive

The service does not request a specific aggregation, so Azure returns its
defaults, and the formatter emits **one event per aggregation present** —
`average`, `total`, `minimum`, `maximum`, `count`. The aggregation is
appended to the metric name and also set as an `aggregation` dimension.

One subscription on `Percentage CPU` can therefore produce:

```
Percentage_CPU.average
Percentage_CPU.maximum
Percentage_CPU.minimum
```

Pick the one you want when building the ITSI KPI. Don't be surprised by
the volume multiplier when estimating ingest.

## KQL Query

| Field | Required | What it must be |
|---|---|---|
| Query Name | yes | Your label; not sent to Splunk |
| KQL Query | yes | Must project a timestamp and ≥1 numeric column |
| Log Analytics Workspace ID | yes | **The workspace GUID**, not the resource ID |
| Schedule Interval (minutes) | no (default 5) | Lookback is `2 ×` this value |
| Splunk Source | no (default `azure:kql`) | Splunk `source` field |
| HEC Target | yes | Edge Processor, from SRE's dropdown |
| Target Index | yes | `test` or `prod` |
| Enabled | — | Unchecked stops execution immediately |

### Workspace ID — GUID, and the dimension cost

Despite the model field being named `workspace_resource_id`, the value is
passed to the Logs Query SDK's `query_workspace(workspace_id=...)`, which
requires the **workspace GUID**. Find it on the workspace's Overview blade
as "Workspace ID":

```
d5a1b2c3-4e5f-6789-0abc-def012345678
```

Supplying the full ARM resource ID makes the query fail.

The trade-off: the formatter *also* parses this field as a resource ID to
build dimensions. A bare GUID has nothing to parse, so every event from a
KQL query arrives with:

- `host` = `unknown`
- `subscription_id`, `resource_group`, `workspace_name` = empty

This is expected, not a misconfiguration. Compensate inside the query
(next section).

### Query shape is the contract

The formatter sorts each result row's columns by type. There is no
mapping UI — what you project is what you get:

| Column | Becomes |
|---|---|
| `TimeGenerated` / `Timestamp` / `timestamp` / `time` | The event timestamp |
| Any numeric column | A Splunk metric (`metric_name:<sanitized>`) |
| Anything else | A Splunk dimension |

Consequences worth stating plainly:

- **No timestamp column → rows are stamped with wall-clock processing
  time.** The query still "succeeds." Latency and trend charts become
  meaningless. Always project `TimeGenerated`.
- **No numeric column → zero metrics, silently.** The run is recorded as
  successful and nothing reaches Splunk.
- The first numeric column also populates Splunk's `_value`.
- Column names are sanitized: non-alphanumeric characters become `_`. So
  `okCount` survives as-is; `ok count` becomes `ok_count`.

Because KQL column names are sanitized rather than derived from Azure,
this is the **one place** you control metric naming. If a metric must
follow SRE's ITSI naming standard, produce it from KQL and name the
column deliberately. See the `splunk-itsi-metrics` skill for the standard.

### A query that works

```kusto
AppRequests
| where TimeGenerated > ago(5m)
| summarize
    requestCount = count(),
    failureCount = countif(Success == false),
    latencyAvgMs = avg(DurationMs)
    by bin(TimeGenerated, 5m)
| extend service = "payments-api", environment = "prod"
```

- `TimeGenerated` → event timestamp
- `requestCount`, `failureCount`, `latencyAvgMs` → three metrics
- `service`, `environment` → dimensions, and the only way to attribute
  these events to a team given the empty workspace dimensions

### Overlap and duplicates

The query runs every 5 minutes with a lookback of
`schedule_interval_minutes × 2` — 10 minutes at the default. Each row is
therefore sent roughly twice.

Bin your results (`by bin(TimeGenerated, 5m)`) so repeats are *identical*
points at the same timestamp, which Splunk handles cleanly. An unbinned
query re-sends slightly different values under different timestamps,
which is much harder to reason about later.

## Target Index and HEC Target

**Target Index** (`test` / `prod`) selects which of your team's two HEC
tokens the service uses. It is set **per subscription and per query**, not
per team — so a team can run some subscriptions against test and others
against prod at the same time.

That's useful for canarying a new subscription. It's also how half a
team's metrics end up stranded in test for a quarter. After promoting,
list your subscriptions and confirm every one reads `prod`.

**HEC Target** picks which Edge Processor receives the events. SRE
manages this list. If a target is disabled by SRE, subscriptions pointing
at it are skipped with a warning — collection stops without any change on
your side.

## Order of operations

1. Terraform applied, role assignments verified
2. **One** metric subscription, on `test`
3. Confirm data in Splunk (within 5 minutes)
4. Add remaining subscriptions and queries
5. Flip each to `prod`
6. Re-audit the list for stragglers still on `test`

Registering thirty subscriptions before verifying one turns a five-minute
field correction into a migration.
