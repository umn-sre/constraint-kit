# Granting SRE's Metric Service Access to Your Azure Telemetry

This directory grants SRE's **Azure Splunk Metric Service** permission to
read your Azure monitoring data so it can forward it to Splunk / ITSI.

It creates **role assignments only**. It does not create, modify, read, or
expose any of your resources. SRE never receives a secret, a service
principal, or a key from you — the service reads from the outside using
its own managed identity, and you control what it can see.

## What gets created

| Resource | Role | Why |
|---|---|---|
| One per `monitored_scopes` entry | `Monitoring Reader` | Read Azure Monitor platform metrics |
| One per `log_analytics_workspace_ids` entry | `Log Analytics Reader` | Run your registered KQL queries |

`Monitoring Reader` is read-only over monitoring data and monitoring
settings. It grants no access to the resources themselves — not their
data, not their configuration, not their keys.

## Before you start

You need **Owner** or **User Access Administrator** on every scope listed
in `monitored_scopes`. `Contributor` is not enough — it cannot create role
assignments. Check first; this is the most common reason an apply fails
partway through.

You also need the metric service's managed identity **object ID**. Read
the next section carefully — this is where most people lose an hour.

## Getting the object ID (not the client ID)

The metrics portal home page displays a **client ID** in a ready-made
`az role assignment create` command. That command works, because the
Azure CLI can look up a service principal by its app ID.

**Terraform cannot.** `principal_id` requires the service principal's
**object ID**. Using the client ID fails with `PrincipalNotFound`.

Convert it once:

```bash
az ad sp show --id <client-id-from-portal> --query id -o tsv
```

Put that value in `metric_service_principal_id`.

<details>
<summary>Alternative: look it up in Terraform instead</summary>

If your applying identity can read the Entra directory, you can resolve
it automatically. Add the `azuread` provider and replace the variable
reference in `main.tf`:

```hcl
terraform {
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
  }
}

data "azuread_service_principal" "metric_service" {
  client_id = var.metric_service_client_id # the ID shown in the portal
}

# then use: principal_id = data.azuread_service_principal.metric_service.object_id
```

This is tidier but adds a provider and a directory-read requirement. The
plain variable is the safer default.
</details>

## Apply

```bash
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars

terraform init
terraform plan     # review every scope before applying
terraform apply
```

Read the plan. Each `azurerm_role_assignment` in it is a standing grant of
read access to SRE — you should recognize and intend every scope listed.

## Choosing scopes

Grant the narrowest scope that covers what you actually want monitored.

| Scope | Form | When |
|---|---|---|
| Single resource | `/subscriptions/<sub>/resourceGroups/<rg>/providers/<provider>/<type>/<name>` | Tight isolation; needs a new entry per resource |
| Resource group | `/subscriptions/<sub>/resourceGroups/<rg>` | **Usually right.** New resources in the group are covered automatically |
| Subscription | `/subscriptions/<sub>` | Only if you truly monitor everything in it |

A subscription-wide grant lets the service read metrics from every
resource in it — including ones someone else creates next year. Prefer
resource groups.

## Verify

```bash
terraform output -raw verification_command | bash
```

You should see one row per scope you granted. If a scope is missing, the
apply didn't cover it.

## Next: register your metrics in the portal

The role assignment lets the service *reach* your resources. It does not
tell it *what to collect* — that's the portal.

Log into the metrics portal and add a metric subscription (or KQL query)
for each thing you want in Splunk. Paste scopes from
`terraform output granted_scopes` as your resource IDs.

Two things to know going in, because they cost real time otherwise:

- **Polling Interval: leave it at 5.** The service runs on a fixed
  5-minute timer for everyone. That field is a *lookback window*, not a
  schedule — raising it to 60 re-sends the same hour of data every 5
  minutes.
- **For KQL, the portal's "Workspace ID" field wants the workspace
  GUID** (the "Workspace ID" on your workspace's Overview blade), *not*
  the full resource ID you put in this Terraform. They're different
  values for the same workspace.

Start with one subscription pointed at the **test** index, confirm the
data lands in Splunk, then add the rest.

## Revoking access

```bash
terraform destroy
```

That removes every role assignment in this configuration. The metric
service will stop being able to read your resources on its next cycle.
Also ask SRE to disable your team's subscriptions so the failures stop
being logged.

## Getting help

- Portal 403 on login, missing HEC target, or a role-mapping change → SRE
- `AuthorizationFailed` on apply → you need Owner or User Access
  Administrator on that scope
- Metrics not appearing in Splunk → check the portal subscription is
  enabled and the resource is inside a granted scope, then contact SRE
