---
name: splunk-itsi-metrics
description: Instrument a UMN service so its metrics land in SRE's Splunk Cloud / ITSI instance — pick what to measure, name metrics and dimensions to SRE's standards, write the HEC emitter code, and verify ingestion. Use this skill whenever work touches Splunk, ITSI, HEC, metric naming, service KPIs, or "how do we monitor this" for a UMN/SRE project, even when the user doesn't say "ITSI" — including reviewing existing metric names for standards compliance, adding telemetry to a new service, wiring metrics out of Azure/OCI/Databricks jobs, or onboarding a service team into ITSI. Also use it when someone asks to add monitoring, observability, or dashboards to a project that SRE supports.
---

# Sending Service Metrics to SRE's Splunk ITSI

## What this skill is for

UMN SRE runs a Splunk Cloud instance with ITSI on top of it. ITSI builds
service health scores out of KPIs, and those KPIs are only as good as the
metrics services feed in. A service that emits well-named metrics gets
entity discovery, thresholding, and service-health rollups nearly for free;
a service that emits sloppily-named metrics produces a metric tree nobody
can navigate and KPIs that can't be split by anything useful.

This skill covers **getting metrics in** — choosing what to emit, naming it
correctly, writing the emitter, and confirming the data arrived. Treat
sending metrics as a standard deliverable of a project, the same way tests
and CI are: if the project runs something in production, it should report
on itself.

## The default path: direct HEC to ITSI

SRE's order of preference for metric sources, best first:

1. **The service POSTs Splunk-format metrics straight to the ITSI HEC.** ← default
2. The service sends to SRE's Edge Processor, which reshapes to standards.
3. A Splunk add-on collects it and sends to the ITSI HEC.
4. Data already on on-prem Splunk, routed over with `mcollect` using
   `source="summaryDataForItsi"`.
5. Event data sent to the Edge Processor and converted to metrics.

Prefer option 1 unless something concrete rules it out. The reason is
freshness and fragility: streamed metrics arrive in ITSI within seconds and
mean exactly what the code says they mean. Anything derived from events has
to go through a scheduled report (no more often than every 5 minutes), so
it is stale on arrival, and it breaks the day someone changes a log line —
that's technical debt bolted onto your alerting.

If the project genuinely can't POST (no egress, a vendor appliance, data
already sitting in on-prem Splunk, an OS-level metric an add-on already
collects), read `references/alternate-paths.md` and pick from there rather
than forcing a bad fit.

## Workflow

### 1. Decide what to measure

Ask what the service promises its users, then measure that. Good starting
set for most services: request/job counts, error or failure counts,
latency or duration, queue depth or backlog age, and a freshness/heartbeat
metric so ITSI can tell "healthy and idle" from "dead." Push back on
metrics that can't drive a KPI or an alert — every metric is a permanent
naming commitment and a line item in someone's dashboard.

Distinguish gauges (a value at a moment: queue depth, latency) from
counters (monotonically accumulating: total requests). Counters are fine to
send — ITSI can rate them — but name them so the consumer knows
(`...Total`), because a counter charted as a gauge looks like a
monotonically rising problem.

### 2. Name the metrics and dimensions

This is the part people get wrong, and it's expensive to fix later because
renaming a metric orphans every KPI and dashboard built on it. Read
`references/naming-standards.md` before writing any names, then validate:

```bash
python scripts/itsi_hec.py validate --names iam.shibboleth.ldap.okCount iam.shibboleth.ldap.responseAvgSec \
  --dimensions host environment role
```

The validator flags illegal characters, missing unit suffixes,
snake_case, and dimension names that look like measurements. It is advisory
where the standard is advisory — treat warnings as a prompt to think, not
as errors to silence.

When the task is **reviewing existing metric names** (a common ask — a team
has already shipped something and wants to know if it conforms), run the
validator over the full list and report findings grouped by problem type,
with a proposed rename for each. Flag which renames are breaking (already
in use by a KPI) versus safe (not yet emitted anywhere).

### 3. Get the token and index from SRE

HEC tokens and Splunk Cloud indexes are **created by SRE**, not by the
service team, and are issued when the team is granted access. Indexes
follow `umn_[cesiUnit]`. If the project doesn't have a token yet, say so
early and keep building against `--dry-run` — the emitter is fully testable
without one.

Never put the token in source, in a container image, or in a Terraform
variable file. Read it from the environment, sourced from whatever secret
store the project already uses: GitHub Actions secrets, Azure Key Vault,
OCI Vault, or Databricks secret scopes. This matters beyond tidiness — a
HEC token is a write credential to a shared, audited platform.

### 4. Write the emitter

`scripts/itsi_hec.py` is a dependency-free (stdlib only) module and CLI
that builds correctly-shaped payloads, validates names, batches, retries,
and POSTs. Prefer importing it or vendoring it into the project over
hand-rolling `requests` calls, so every service fails the same way and
emits the same shape:

```python
from itsi_hec import MetricSender

sender = MetricSender(
    url="https://http-inputs.itsi-umn.splunkcloud.com:443/services/collector",
    token=os.environ["ITSI_HEC_TOKEN"],
    source="ent:psoft:cdcJob",
)
sender.add(
    metrics={"ents.psoft.cdc.rowsProcessedTotal": 14820,
             "ents.psoft.cdc.lagSec": 3.2},
    dimensions={"environment": "prd", "role": "extractor", "entity": "psoft-cdc-01"},
)
sender.flush()
```

Shape rules the module already handles, worth knowing anyway:
`"event": "metric"`, measurements go in `fields` as
`"metric_name:<name>": <float>`, dimensions go in the same `fields` dict as
strings, and `host`/`source`/`sourcetype`/`time` sit at the top level. Many
data points share one payload when they share dimensions; the body is a
list of such payloads.

Operational points that decide whether this survives contact with
production:

- **Never let telemetry take down the thing it measures.** Emit on a
  timeout, catch and log failures, and continue. The module defaults to a
  short timeout and non-raising `flush()` for this reason.
- **Batch.** One POST per data point wastes connections and hits rate
  limits. Accumulate a batch and flush on an interval (30–60s is a sane
  default) or at end of job.
- **Size limits.** Splunk Cloud HEC tops out at 2GB per request; on-prem is
  ~5MB. The module chunks well below that — don't raise the chunk size
  without a reason.
- **Timestamps.** Send `time` explicitly as epoch seconds for the moment
  the measurement was taken, not the moment it was sent, or batching skews
  your latency charts.
- **Long-running services** emit on a timer. **Batch jobs and CI steps**
  emit once at the end, including a success/failure metric — otherwise a
  job that dies early is indistinguishable from a job that never ran.

For the exact endpoints (event vs. multi-line vs. raw, and Edge Processor
hosts), see `references/endpoints.md`.

### 5. Verify it landed

Ingestion is not done until someone has seen the data in Splunk:

1. Open the [Analytics Workspace](https://itsi.itsi-umn.splunkcloud.com/en-US/app/search/analytics_workspace).
2. Metrics section → **+ Add new filter** → select the index → **Apply**.
3. The tree opens with the CESI unit at the top; expand to find the metric.
4. Split the chart by a dimension to confirm dimensions came through as
   labels and not as measurements.

If a metric is missing, the usual causes in order: token not authorized for
that index, the value wasn't numeric (a string measurement is silently
useless), the name has an illegal character, or the payload was posted to
`/raw` instead of `/services/collector`. `scripts/itsi_hec.py send
--dry-run` prints the exact JSON body, which settles most of these fast.

### 6. Hand it off

Leave the project with: the metric names and their meaning, the index and
source used, where the token comes from, the emit cadence, and what a
sensible alert threshold might be. The service team owns the KPIs built on
these metrics in ITSI, so they need to know what each number actually
counts.

## Reference files

- `references/naming-standards.md` — metric and dimension naming rules,
  unit suffixes, worked examples. Read before naming anything.
- `references/endpoints.md` — ITSI and Edge Processor endpoints, payload
  shape, size limits, token handling, verification.
- `references/alternate-paths.md` — Edge Processor, Splunk add-ons, and
  on-prem `mcollect` routing, for when direct HEC isn't possible.

## Scripts

- `scripts/itsi_hec.py` — stdlib-only sender + name validator.
  `validate` checks names; `send` posts a JSON file or stdin (`--dry-run`
  prints the body instead). Import `MetricSender` to embed it in a service.
