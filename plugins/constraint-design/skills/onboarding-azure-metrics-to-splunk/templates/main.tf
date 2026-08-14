# Grants SRE's Azure Splunk Metric Service read-only access to this team's
# telemetry. Nothing here creates, modifies, or exposes any resource — it only
# creates role assignments for an identity SRE owns.
#
# Revoking is `terraform destroy` in this directory. Nothing else depends on it.

terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
}

# Platform metrics (Azure Monitor).
#
# Monitoring Reader is read-only over monitoring data and monitoring settings.
# It grants NO access to the resources themselves — not their data, not their
# configuration, not their keys.
resource "azurerm_role_assignment" "monitoring_reader" {
  for_each = toset(var.monitored_scopes)

  scope                = each.value
  role_definition_name = "Monitoring Reader"
  principal_id         = var.metric_service_principal_id

  # The identity is a service principal, not a user. Setting this explicitly
  # avoids a lookup that requires directory read permission the applying
  # identity may not have.
  principal_type = "ServicePrincipal"

  description = "SRE Azure Splunk Metric Service - platform metric collection"
}

# KQL queries against Log Analytics.
#
# Only needed if this team registers KQL queries in the portal. Leave
# `log_analytics_workspace_ids` empty otherwise — do not grant access to a
# workspace nobody is querying.
resource "azurerm_role_assignment" "log_analytics_reader" {
  for_each = toset(var.log_analytics_workspace_ids)

  scope                = each.value
  role_definition_name = "Log Analytics Reader"
  principal_id         = var.metric_service_principal_id
  principal_type       = "ServicePrincipal"

  description = "SRE Azure Splunk Metric Service - KQL query execution"
}
