# Used to call the AWS account ID
data "aws_caller_identity" "current" {}

# Enabling CloudTrail
resource "aws_cloudtrail" "cloudtrail" {
  name                          = "${var.prefix_name}-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.ct-bucket.id
  s3_key_prefix                 = "prefix"
  include_global_service_events = true
}