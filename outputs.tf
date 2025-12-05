# Root Module Outputs
# Aggregates outputs from child modules

# CloudTrail Outputs

output "cloudtrail_trail_arn" {
  description = "ARN of the CloudTrail trail"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].trail_arn : null
}

output "cloudtrail_trail_id" {
  description = "ID of the CloudTrail trail"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].trail_id : null
}

output "cloudtrail_bucket_name" {
  description = "Name of the S3 bucket for CloudTrail logs"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].s3_bucket_name : null
}

output "cloudtrail_bucket_arn" {
  description = "ARN of the S3 bucket for CloudTrail logs"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].s3_bucket_arn : null
}

output "cloudtrail_kms_key_id" {
  description = "ID of the KMS key for CloudTrail encryption"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].kms_key_id : null
}

output "cloudtrail_kms_key_arn" {
  description = "ARN of the KMS key for CloudTrail encryption"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].kms_key_arn : null
}

output "cloudtrail_cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for CloudTrail"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].cloudwatch_log_group_name : null
}

output "cloudtrail_sns_topic_arn" {
  description = "ARN of the SNS topic for CloudTrail alerts"
  value       = var.enable_cloudtrail ? module.cloudtrail[0].sns_topic_arn : null
}

# AWS Config Outputs

output "config_recorder_name" {
  description = "Name of the AWS Config configuration recorder"
  value       = var.enable_config ? module.config[0].recorder_name : null
}

output "config_recorder_id" {
  description = "ID of the AWS Config configuration recorder"
  value       = var.enable_config ? module.config[0].recorder_id : null
}

output "config_bucket_name" {
  description = "Name of the S3 bucket for Config snapshots"
  value       = var.enable_config ? module.config[0].s3_bucket_name : null
}

output "config_bucket_arn" {
  description = "ARN of the S3 bucket for Config snapshots"
  value       = var.enable_config ? module.config[0].s3_bucket_arn : null
}

output "config_delivery_channel_id" {
  description = "ID of the AWS Config delivery channel"
  value       = var.enable_config ? module.config[0].delivery_channel_id : null
}

output "config_kms_key_id" {
  description = "ID of the KMS key for Config encryption"
  value       = var.enable_config ? module.config[0].kms_key_id : null
}

output "config_kms_key_arn" {
  description = "ARN of the KMS key for Config encryption"
  value       = var.enable_config ? module.config[0].kms_key_arn : null
}

output "config_iam_role_arn" {
  description = "ARN of the IAM role for AWS Config"
  value       = var.enable_config ? module.config[0].iam_role_arn : null
}

# GuardDuty Outputs

output "guardduty_detector_id" {
  description = "ID of the GuardDuty detector"
  value       = var.enable_guardduty ? module.guardduty[0].detector_id : null
}

output "guardduty_detector_arn" {
  description = "ARN of the GuardDuty detector"
  value       = var.enable_guardduty ? module.guardduty[0].detector_arn : null
}

output "guardduty_account_id" {
  description = "AWS account ID where GuardDuty is enabled"
  value       = var.enable_guardduty ? module.guardduty[0].account_id : null
}

# Detective Outputs

output "detective_graph_id" {
  description = "ID of the Detective graph"
  value       = var.enable_detective ? module.detective[0].graph_id : null
}

output "detective_graph_arn" {
  description = "ARN of the Detective graph"
  value       = var.enable_detective ? module.detective[0].graph_arn : null
}

# Security Hub Outputs

output "securityhub_account_arn" {
  description = "ARN of the Security Hub account"
  value       = var.enable_securityhub ? module.securityhub[0].account_arn : null
}

output "securityhub_account_id" {
  description = "ID of the Security Hub account"
  value       = var.enable_securityhub ? module.securityhub[0].account_id : null
}

output "securityhub_enabled_standards" {
  description = "Map of enabled Security Hub standards"
  value       = var.enable_securityhub ? module.securityhub[0].enabled_standards : null
}

output "securityhub_standards_subscriptions" {
  description = "Map of Security Hub standards subscription ARNs"
  value       = var.enable_securityhub ? module.securityhub[0].standards_subscriptions : null
}