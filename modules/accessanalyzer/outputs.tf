# IAM Access Analyzer Module - Outputs

output "external_analyzer_arn" {
  description = "ARN of the external access analyzer"
  value       = aws_accessanalyzer_analyzer.external.arn
}

output "external_analyzer_id" {
  description = "ID of the external access analyzer"
  value       = aws_accessanalyzer_analyzer.external.id
}

output "unused_analyzer_arn" {
  description = "ARN of the unused access analyzer (if enabled)"
  value       = var.enable_unused_access_analyzer ? aws_accessanalyzer_analyzer.unused[0].arn : null
}

output "unused_analyzer_id" {
  description = "ID of the unused access analyzer (if enabled)"
  value       = var.enable_unused_access_analyzer ? aws_accessanalyzer_analyzer.unused[0].id : null
}

output "account_id" {
  description = "AWS account ID where Access Analyzer is enabled"
  value       = data.aws_caller_identity.current.account_id
}
