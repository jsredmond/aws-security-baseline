# Amazon Inspector Module - Outputs

output "account_id" {
  description = "AWS account ID where Inspector is enabled"
  value       = data.aws_caller_identity.current.account_id
}

output "enabled_resource_types" {
  description = "List of resource types enabled for Inspector scanning"
  value       = var.resource_types
}
