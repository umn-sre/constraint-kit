output "granted_scopes" {
  description = "Scopes where SRE's metric service can now read platform metrics. Paste these into the portal as your metric subscription resource IDs."
  value       = var.monitored_scopes
}

output "granted_workspaces" {
  description = "Log Analytics workspaces the metric service can now query."
  value       = var.log_analytics_workspace_ids
}

output "verification_command" {
  description = "Run this to confirm the role assignments exist as expected."
  value       = "az role assignment list --assignee ${var.metric_service_principal_id} --all --output table"
}
