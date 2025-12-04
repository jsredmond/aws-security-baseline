output "account_arn" {
  description = "ARN of the Security Hub account"
  value       = aws_securityhub_account.main.arn
}

output "account_id" {
  description = "ID of the Security Hub account"
  value       = aws_securityhub_account.main.id
}

output "enabled_standards" {
  description = "Map of enabled Security Hub standards"
  value       = local.enabled_standards
}

output "standards_subscriptions" {
  description = "Map of Security Hub standards subscription ARNs"
  value       = { for k, v in aws_securityhub_standards_subscription.standards : k => v.standards_subscription_arn }
}
