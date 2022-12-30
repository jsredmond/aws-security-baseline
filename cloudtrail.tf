# Used to call the AWS account ID
data "aws_caller_identity" "current" {}

# KMS key to encrypt CloudWatch log group
resource "aws_kms_key" "ctkey" {
  description             = "This key is used to encrypt an eks cloudwatch log group"
  deletion_window_in_days = 7
}

# Create CloudWatch log group for CloudTrail
resource "aws_cloudwatch_log_group" "cloudwatch-ct-logs" {
  name              = "cloudwatch-ct-logs"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.ctkey.arn
}

# Enabling CloudTrail
resource "aws_cloudtrail" "cloudtrail" {
  name                          = "${var.prefix_name}-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.ct-bucket.id
  s3_key_prefix                 = "prefix"
  include_global_service_events = true
  enable_log_file_validation    = true
  is_multi_region_trail         = true
  kms_key_id                    = aws_kms_key.s3key.arn
  cloud_watch_logs_group_arn    = "${aws_cloudwatch_log_group.cloudwatch-ct-logs.arn}:*"

}