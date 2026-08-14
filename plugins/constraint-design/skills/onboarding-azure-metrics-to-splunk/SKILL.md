---
name: onboarding-azure-metrics-to-splunk
description: Use when a team wants their Azure metrics or Log Analytics data flowing into SRE's Splunk/ITSI via the Azure Splunk Metric Service — granting Monitoring Reader or Log Analytics Reader to the service's managed identity, standing up the customer-side Terraform repo of role assignments, registering metric subscriptions or KQL queries in the portal, or debugging why Azure metrics never showed up in Splunk. Also use when someone asks "how do we get our Azure metrics into ITSI", mentions the metrics portal, HEC targets, metric subscriptions, or the metric service's managed identity.
---

# Onboarding a Team's Azure Metrics into Splunk

## What this skill is for

SRE runs the **Azure Splunk Metric Service** — a pull-based platform that
reads Azure Monitor metrics and Log Analytics KQL results on a timer,
reshapes them into Splunk HEC metric events, and posts them to Edge
Processors that forward to Splunk Cloud / ITSI.

"Pull-based" is the whole point: **no secrets cross the boundary.** The
customer never hands over a service principal, a client secret, or a HEC
token. They grant one Azure role to SRE's managed identity, and the
service reads from the outside in.

This skill covers **the customer half** of that: the RBAC grant, the
Terraform repo that owns it, the portal registration, and verification.
It is deliberately small — the customer's total work is one Terraform
apply and a few portal forms. Most of this skill's value is in the
handful of ways that small job silently goes wrong.

**Related:** for choosing *what* to measure and how to name metrics to
SRE's ITSI standards, use the `splunk-itsi-metrics` skill. This skill
gets Azure's *existing* metrics flowing; that skill governs custom
metrics a service emits itself. Read the naming caveat in
[Gotcha 5](#5-splunk-metric-names-are-not-yours-to-choose) before
promising anyone a metric name.

## Who owns what

Be clear about this before starting — most onboarding stalls are someone
waiting on the other party.

| Thing | Owner | How the customer gets it |
|---|---|---|
| Metric team record, HEC tokens (test + prod) | **SRE admin** | Ask; created before the customer can log in |
| Entra group → team role mapping | **SRE admin** | Ask; without it the portal 403s |
| HEC targets (Edge Processor URLs) | **SRE admin** | Appears as a dropdown in the portal |
| Managed identity + its object ID | **SRE** | Portal home page shows the client ID; see Gotcha 1 |
| RBAC grant on customer resources | **Customer** | Terraform in their own repo — this skill's scaffold |
| Metric subscriptions and KQL queries | **Customer** | Portal forms |
| Log Analytics workspace, diagnostic settings | **Customer** | Pre-existing; the service does not create them |

## Before you start

Confirm all four. If any is missing, stop and go get it — every one of
them blocks the next step, and discovering it three steps later costs an
afternoon.

1. **The team exists in the portal** and the customer can log in and see
   their team home page. If they get a 403, the Entra group role mapping
   is missing — that's an SRE admin fix, not a customer fix.
2. **The managed identity's object ID** (not the client ID — Gotcha 1).
3. **Owner or User Access Administrator** on the scope being granted.
   `Contributor` cannot create role assignments. This is the single most
   common surprise; check it before writing any Terraform.
4. **The resources actually emit the metrics** the team wants. Azure
   platform metrics exist automatically; anything from Log Analytics
   requires diagnostic settings the customer already configured.

## Workflow

### 1. Pick the scope and the collection method

Two paths, and a team can use both:

**Platform metrics** — anything Azure Monitor already exposes for a
resource (CPU, request counts, queue depth). No setup on the resource,
just RBAC plus a portal subscription. Prefer this whenever it covers the
need; it is strictly less to maintain.

**KQL queries** — for anything platform metrics can't express: a value
computed across log tables, an app-specific counter, a business metric.
Costs more (a query runs every cycle) and carries the sharpest edges in
this skill. Use it when platform metrics genuinely don't have the number.

Then choose the RBAC **scope** — the narrowest thing that covers what
they want to monitor, in this order of preference:

1. A single resource — best isolation, but a new role assignment for
   every new resource.
2. A resource group — the usual right answer. Resources added to the
   group are covered automatically.
3. A subscription — only when the team genuinely monitors everything in
   it. Grants read on resources they may not intend to share.

Scope is a security decision, not a convenience one. A subscription-wide
`Monitoring Reader` lets the service read metrics from every resource in
it, forever, including ones created next year by someone else.

### 2. Stand up the customer's Terraform repo

The role assignment belongs in the **customer's** infrastructure repo, not
SRE's. It grants access to their resources, in their subscription, under
their change control — SRE should never hold `Owner` on a customer
subscription just to wire up monitoring.

Copy `templates/` into the customer repo (`terraform/splunk-metrics/` is
a good home) and fill in `terraform.tfvars`:

```bash
cp -r templates/ <customer-repo>/terraform/splunk-metrics/
cd <customer-repo>/terraform/splunk-metrics
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars — see templates/README.md for each variable
terraform init
terraform plan
terraform apply
```

The template creates `Monitoring Reader` on each monitored scope, and
optionally `Log Analytics Reader` on each workspace the team runs KQL
against. It is intentionally tiny — two resource types and a handful of
variables. Resist the urge to fold it into an existing module; keeping it
standalone makes it obvious what SRE can read and trivial to revoke.

If the customer has no Terraform at all and won't adopt it for this,
`templates/README.md` has the equivalent `az` commands. Prefer Terraform
— an untracked role assignment is invisible at audit time and nobody
remembers who ran the CLI command.

### 3. Register subscriptions and queries in the portal

The customer does this themselves at the portal's team pages. Each
metric subscription needs a resource ID, metric namespace, metric names,
polling interval, Splunk source, HEC target, and target index.

Read `references/portal-registration.md` before filling in the first
one — it documents every field, what the service actually does with it,
and the values that look reasonable but misbehave (notably the polling
interval, Gotcha 2, and the workspace ID, Gotcha 3).

Start with **one** subscription against **one** resource, targeting the
**test** index. Verify it end to end before adding the rest. A bad field
value in a single subscription is a five-minute fix; the same mistake
copied across thirty subscriptions is a migration.

### 4. Verify data landed

Onboarding is not done until someone has seen the metric in Splunk. The
service runs on a **fixed 5-minute timer**, so the first data point
arrives within 5 minutes of saving the subscription — if it doesn't,
something is wrong; waiting longer will not fix it.

1. Open the Analytics Workspace in Splunk.
2. Add a filter for the team's index (test first).
3. Find the metric under its sanitized name — `Percentage CPU` arrives as
   `Percentage_CPU.average`, not as you typed it (Gotcha 5).
4. Split by `resource_name` or `resource_group` to confirm dimensions
   came through.

Nothing there after two cycles? Work `references/troubleshooting.md` in
order — it's sequenced by how often each cause is the real one, and the
first two account for most cases.

### 5. Promote to prod and hand off

Once test data looks right, edit each subscription's **Target Index** to
`prod`. That switches which HEC token the service uses; nothing else
changes. Consider leaving a low-volume subscription on test as a canary.

Leave the team with: which resources and metrics are collected, the
Splunk index and source values, where the Terraform lives, who to ask for
a HEC target or role-mapping change, and what a sensible ITSI alert
threshold looks like. They own the KPIs built on this data — they need to
know what each number counts.

## Gotchas

These are the failure modes worth internalizing. Each one is confirmed
against the service's source, and each produces a **silent** failure or a
misleading error rather than a clear one.

### 1. The portal shows a client ID; Terraform needs the object ID

The portal home page renders the managed identity's **client ID** into an
`az role assignment create --assignee` command. That command works — the
CLI resolves a service principal by app ID.

**Terraform does not.** `azurerm_role_assignment.principal_id` requires
the service principal's **object ID**. Pasting the client ID there fails
with `PrincipalNotFound`, or worse, silently targets nothing meaningful.

Convert it once:

```bash
az ad sp show --id <client-id-from-portal> --query id -o tsv
```

That object ID is what goes in `terraform.tfvars`. `templates/README.md`
also shows an `azuread` data-source variant that does the lookup in
Terraform, if the customer can read the directory.

### 2. Polling interval is a lookback window, not a schedule

The field is labeled "Polling Interval (minutes)" and accepts 1–60. It
does **not** change how often anything runs. The function's timer is hard
-coded to `0 */5 * * * *` — every 5 minutes, for everyone.

That value is passed as the Azure Monitor query's *lookback window*. So
setting it to 60 means: every 5 minutes, pull the last 60 minutes of
data. The same data points get re-sent roughly 12 times.

**Leave it at 5.** The only reason to raise it is a metric Azure
populates on a slower cadence, and then accept the duplicates knowingly.
Lowering it below 5 creates gaps.

### 3. The KQL workspace field wants a GUID, and costs you dimensions

The portal labels it "Log Analytics Workspace ID" and the model calls it
`workspace_resource_id`. The service passes it straight to the Logs Query
SDK's `query_workspace(workspace_id=...)`, which requires the
**workspace GUID** — the "Workspace ID" on the workspace's Overview
blade, not the `/subscriptions/.../workspaces/...` ARM resource ID.

Supply the ARM resource ID and the query fails. Supply the GUID and the
query works — but the formatter also tries to parse that same field as a
resource ID to derive dimensions. A bare GUID has no slashes to parse, so
every query's events arrive with `host` set to `unknown` and
`subscription_id`, `resource_group`, and `workspace_name` **empty**.

Use the GUID, and put the identifying information in the query itself:

```kusto
AppRequests
| where TimeGenerated > ago(5m)
| summarize failures = countif(Success == false) by bin(TimeGenerated, 5m)
| extend service = "payments-api", environment = "prod"
```

`service` and `environment` are non-numeric, so they become Splunk
dimensions. That's the only reliable way to tell one team's KQL metrics
from another's.

### 4. KQL result shape decides what becomes a metric

The formatter walks each result row and sorts columns by type. There is
no configuration for this — the query's projection *is* the contract:

- A column named `TimeGenerated` (or `Timestamp`/`timestamp`/`time`)
  becomes the event timestamp. **Without one, rows are stamped with
  wall-clock processing time**, which quietly ruins any latency or
  trend chart.
- Every **numeric** column becomes a metric.
- Every other column becomes a **dimension**.

So a query returning zero numeric columns produces zero metrics and
fails silently — it looks like it ran fine. Always project at least one
number and a `TimeGenerated`.

Also note the query's lookback is `schedule_interval_minutes * 2` while
the timer fires every 5 minutes, so rows are re-sent about twice.
Aggregate with `bin(TimeGenerated, 5m)` so the duplicates are identical
points rather than smeared values.

### 5. Splunk metric names are not yours to choose

Names are derived, then sanitized: every non-alphanumeric character
becomes `_`, and platform metrics get the aggregation appended.
`Percentage CPU` becomes `Percentage_CPU.average`. One event is emitted
per available aggregation, so a single Azure metric can arrive as
`.average`, `.total`, `.minimum`, `.maximum`, and `.count`.

Two consequences worth stating out loud to the team:

- **Don't promise an ITSI naming-standard-compliant name for pulled
  Azure metrics.** These names come from Azure and cannot conform to the
  dot-delimited camelCase convention in `splunk-itsi-metrics`. Build the
  ITSI KPI on the name that actually arrives.
- **KQL column names are the one place naming is controllable.** They're
  sanitized the same way, so a column named `okCount` survives intact
  while `ok count` becomes `ok_count`. If a metric must match SRE
  standards, produce it from KQL and name the column carefully.

### 6. Test and prod are one field, not two environments

`Target Index` on each subscription and query selects which of the
team's two HEC tokens the service uses. It is per-subscription, not
per-team — a team can have some subscriptions on test and others on
prod simultaneously. That's useful for canarying, and it's also how
someone accidentally leaves half their metrics in test for a quarter.
Audit the list after promoting.

## Quick reference

| Symptom | Most likely cause |
|---|---|
| Portal returns 403 at login | Entra group role mapping missing (SRE admin) |
| `PrincipalNotFound` on apply | Client ID used where object ID is required (Gotcha 1) |
| `AuthorizationFailed` on apply | Customer lacks Owner / User Access Administrator on the scope |
| No metrics after 10+ minutes | RBAC scope doesn't cover the resource, or subscription disabled |
| Metric arrives, dimensions empty | KQL workspace given as GUID — expected (Gotcha 3) |
| KQL query "succeeds", no data in Splunk | No numeric column in the projection (Gotcha 4) |
| Duplicate / stair-stepped data points | Polling interval raised above 5 (Gotcha 2) |
| Timestamps all bunched at collection time | KQL missing `TimeGenerated` (Gotcha 4) |
| Can't find the metric by name in Splunk | Name was sanitized and suffixed (Gotcha 5) |

## Files

- `templates/` — drop-in Terraform for the customer's repo:
  `main.tf`, `variables.tf`, `outputs.tf`, `terraform.tfvars.example`,
  and a `README.md` written for the customer team (not for SRE).
- `references/portal-registration.md` — every portal field, what the
  service does with it, and how to fill it in.
- `references/troubleshooting.md` — ordered diagnostic path for "the
  metrics never showed up."
