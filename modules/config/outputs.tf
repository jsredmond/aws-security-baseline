# AWS Config Module - Outputs

output "recorder_name" {
  description = "Name of the AWS Config configuration recorder"
  value       = aws_config_configuration_recorder.main.name
}

output "recorder_id" {
  description = "ID of the AWS Config configuration recorder"
  value       = aws_config_configuration_recorder.main.id
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Config snapshots"
  value       = aws_s3_bucket.config.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for Config snapshots"
  value       = aws_s3_bucket.config.arn
}

output "delivery_channel_id" {
  description = "ID of the AWS Config delivery channel"
  value       = aws_config_delivery_channel.main.id
}

output "kms_key_id" {
  description = "ID of the KMS key for Config encryption"
  value       = aws_kms_key.config.id
}

output "kms_key_arn" {
  description = "ARN of the KMS key for Config encryption"
  value       = aws_kms_key.config.arn
}

output "iam_role_arn" {
  description = "ARN of the IAM role for AWS Config"
  value       = aws_iam_role.config.arn
}
