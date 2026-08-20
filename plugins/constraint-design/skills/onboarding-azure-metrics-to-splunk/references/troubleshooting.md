# Troubleshooting: The Metrics Never Showed Up

Work these in order. They're sequenced by how often each is the actual
cause, and each step is cheap enough that skipping ahead rarely pays.

**First, calibrate expectations.** The service runs on a fixed 5-minute
timer. If nothing has arrived after **two cycles (10 minutes)**, something
is wrong — waiting longer will not fix it. Conversely, don't start
debugging at minute three.

## 1. Is the subscription enabled and pointed at the right index?

The cheapest check, and a genuinely common cause.

In the portal, open the subscription or query and confirm:

- **Enabled** is checked. Disabled records are skipped silently.
- **Target Index** matches the index you're searching in Splunk. Looking
  in `prod` for data being sent to `test` produces exactly the symptom
  "no data," and people lose hours to it.
- **HEC Target** is one SRE currently has enabled. If SRE disabled that
  Edge Processor, your subscription is skipped with a warning and nothing
  on your side changed.

## 2. Does the RBAC grant actually cover the resource?

```bash
az role assignment list \
  --assignee <metric-service-object-id> \
  --scope "<the-resource-id-from-your-subscription>" \
  --include-inherited \
  --output table
```

`--include-inherited` matters: a resource-group grant covers resources
inside it, and without the flag you'll wrongly conclude nothing is
granted.

You want `Monitoring Reader` (for platform metrics) or `Log Analytics
Reader` (for KQL) in the output. If it's empty:

- The resource is outside every scope in `monitored_scopes`. Add it and
  re-apply.
- Or the assignment was made against the **client ID** instead of the
  object ID, so it exists but references nothing useful. Re-check with
  `az ad sp show --id <client-id> --query id -o tsv` and compare.

Role assignments can take a minute or two to propagate. If you applied
seconds ago, give it one more cycle before digging further.

## 3. Are you searching for the right metric name?

Names are transformed on the way in. `Percentage CPU` arrives in Splunk as
`Percentage_CPU.average` — every non-alphanumeric character becomes `_`,
and the aggregation is appended.

In the Splunk Analytics Workspace, browse the metric tree for the index
rather than searching for the name you typed. Filter by the `source` value
from the subscription (`azure:metric` by default) to narrow it.

If you find the metric under a different name than expected, that's not a
bug — that's step 3 resolving successfully. Build your KPI on the name
that arrives.

## 4. Does Azure actually have this metric, under this name?

A metric name Azure doesn't recognize returns no data without raising an
obvious error.

```bash
az monitor metrics list-definitions \
  --resource "<resource-id>" \
  --query "[].{name:name.value, namespace:namespace}" -o table
```

Confirm both the **exact spelling** (spaces and capitals included) and the
**namespace**. Then confirm the metric currently has data — a metric that
exists but has had no activity in the window returns empty:

```bash
az monitor metrics list \
  --resource "<resource-id>" \
  --metric "<Metric Name>" \
  --interval PT5M \
  --output table
```

If this returns nothing, the service will also return nothing. The problem
is upstream of Splunk entirely.

## 5. KQL only: is the query producing metric-shaped rows?

Run the query in the Log Analytics blade and inspect the **result
columns**, not just whether it succeeds.

- **Is there a numeric column?** Without one, zero metrics are produced
  and the run is still recorded as successful. This is the most common
  KQL failure and the least visible.
- **Is there a `TimeGenerated` column?** Without one, rows are stamped
  with processing time. Data appears, but bunched at collection instants
  instead of spread across the window — if your chart looks like vertical
  stripes, this is why.
- **Did you use the workspace GUID?** The portal field needs the GUID from
  the workspace Overview blade, not the ARM resource ID. A resource ID
  makes the query fail outright.
- **Does the query return rows for a 10-minute window?** The service uses
  `schedule_interval_minutes × 2` as its lookback. A query filtered to
  `ago(1h)` behaves differently there than in your ad-hoc testing.

Also confirm `Log Analytics Reader` is granted on the workspace — step 2's
check, but people frequently grant `Monitoring Reader` only and assume KQL
is covered.

## 6. Empty dimensions on KQL events

If events arrive but `host` is `unknown` and `subscription_id`,
`resource_group`, and `workspace_name` are blank:

**This is expected.** The workspace field holds a GUID, which the
formatter cannot parse into those dimensions. It is not a
misconfiguration and there's no setting that fixes it.

Add identifying columns to the query instead:

```kusto
| extend service = "payments-api", environment = "prod"
```

Non-numeric columns become dimensions, so these come through as labels
you can split on.

## 7. Duplicate or stair-stepped data points

Almost always the polling interval.

The timer is fixed at 5 minutes. The subscription's polling interval sets
the **lookback window**, so a value of 60 pulls the last hour every 5
minutes — the same points, a dozen times over.

Set it back to 5. For KQL, the equivalent is the built-in `2 ×` lookback
overlap; bin the results (`by bin(TimeGenerated, 5m)`) so repeats are
identical points rather than slightly different ones.

## 8. Still nothing — escalate to SRE

By this point you've ruled out everything on the customer side. Ask SRE to
check the function's Application Insights logs for your team.

Bring:

- Team display name as it appears in the portal
- The subscription or query ID
- Full Azure resource ID (or workspace GUID)
- Target index and HEC target name
- Output of the `az role assignment list` command from step 2
- Roughly when you saved the config

SRE-side causes you cannot see or fix:

- HEC token invalid or not authorized for that index
- Edge Processor unreachable or dropping events at its filter stage
- Function App failing or timing out before reaching your team — the
  orchestrator isolates failures per team, so one team's breakage
  shouldn't affect yours, but a global failure affects everyone
- The Edge Processor's fine-grained filter rules dropping your metric
  before it reaches the indexer — worth asking about explicitly if
  everything else checks out, since it produces a perfect "posted
  successfully, never indexed" signature

## Quick index

| Symptom | Step |
|---|---|
| Nothing at all, subscription looks fine | 1, 2 |
| `PrincipalNotFound` when applying Terraform | 2 (client ID vs object ID) |
| `AuthorizationFailed` when applying Terraform | You need Owner / User Access Administrator on that scope |
| Portal 403 at login | Entra group role mapping missing — SRE fix |
| Can't find the metric by the name you typed | 3 |
| Some metrics arrive, one doesn't | 4 |
| KQL "runs fine," no data in Splunk | 5 |
| KQL data has no dimensions | 6 |
| Timestamps bunched into stripes | 5 (missing `TimeGenerated`) |
| Duplicate points | 7 |
| Everything checks out | 8 |
