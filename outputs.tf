output "cloudtrail_bucket_name" {
  description = "Name of the S3 bucket used for CloudTrail logs"
  value       = aws_s3_bucket.cloudtrail_bucket.bucket
}

output "config_recorder_name" {
  description = "The name of the AWS Config recorder"
  value       = aws_config_configuration_recorder.config_rec.name
}

output "securityhub_account_arn" {
  description = "ARN of the enabled AWS Security Hub account"
  value       = aws_securityhub_account.security_hub.arn
}

output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = aws_guardduty_detector.detector.id
}

output "detective_graph_id" {
  description = "ID of the Amazon Detective graph"
  value       = aws_detective_graph.detective.id
}