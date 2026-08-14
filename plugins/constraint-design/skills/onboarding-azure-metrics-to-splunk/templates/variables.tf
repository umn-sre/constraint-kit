variable "subscription_id" {
  description = "Your Azure subscription ID — the one containing the resources to be monitored."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-fA-F-]{36}$", var.subscription_id))
    error_message = "subscription_id must be a GUID."
  }
}

variable "metric_service_principal_id" {
  description = <<-EOT
    The OBJECT ID of SRE's metric service managed identity.

    This is NOT the client ID shown on the portal home page. Convert it once:

      az ad sp show --id <client-id-from-portal> --query id -o tsv

    Using the client ID here fails with PrincipalNotFound.
  EOT
  type        = string

  validation {
    condition     = can(regex("^[0-9a-fA-F-]{36}$", var.metric_service_principal_id))
    error_message = "metric_service_principal_id must be a GUID (the object ID, not the client ID)."
  }
}

variable "monitored_scopes" {
  description = <<-EOT
    Scopes to grant Monitoring Reader on. Use the narrowest scope that covers
    what you actually want monitored — a resource group is usually right.

    Resource group:
      /subscriptions/<sub>/resourceGroups/<rg>
    Single resource:
      /subscriptions/<sub>/resourceGroups/<rg>/providers/<provider>/<type>/<name>
    Whole subscription (grants read on everything in it, now and in future):
      /subscriptions/<sub>
  EOT
  type        = list(string)

  validation {
    condition     = length(var.monitored_scopes) > 0
    error_message = "Provide at least one scope — otherwise this configuration grants nothing."
  }

  validation {
    condition     = alltrue([for s in var.monitored_scopes : startswith(s, "/subscriptions/")])
    error_message = "Each scope must be a full ARM resource ID starting with /subscriptions/."
  }
}

variable "log_analytics_workspace_ids" {
  description = <<-EOT
    Full ARM resource IDs of Log Analytics workspaces this team runs KQL
    queries against. Leave empty if not using KQL queries.

    Note: this takes the full RESOURCE ID. The portal's KQL form takes the
    workspace GUID instead — they are different values for the same workspace.
    See the skill's Gotcha 3.

      /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<name>
  EOT
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for w in var.log_analytics_workspace_ids :
      can(regex("/providers/Microsoft.OperationalInsights/workspaces/", w))
    ])
    error_message = "Each entry must be a full Log Analytics workspace resource ID, not a workspace GUID."
  }
}
