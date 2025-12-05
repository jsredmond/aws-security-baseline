# CloudTrail Module - Main Resources
# This module deploys AWS CloudTrail with multi-region logging, encryption, CloudWatch integration, and SNS notifications

# Data sources for account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random ID for unique bucket naming
resource "random_id" "suffix" {
  byte_length = 8
}

# Locals for computed values
locals {
  service_name        = "cloudtrail"
  bucket_name         = "${var.environment}-${local.service_name}-${random_id.suffix.dec}"
  cloudwatch_log_name = "${var.environment}-${local.service_name}-logs"

  common_tags = merge(
    var.common_tags,
    {
      Name        = "${var.environment}-${local.service_name}"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = "cloudtrail"
    }
  )
}

# KMS key for CloudWatch log group encryption
resource "aws_kms_key" "cloudwatch" {
  description             = "KMS key for CloudTrail CloudWatch log group encryption"
  enable_key_rotation     = true
  deletion_window_in_days = var.kms_key_deletion_window

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "cloudwatch-log-key-policy"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

# KMS key for CloudTrail and SNS encryption
resource "aws_kms_key" "cloudtrail" {
  description             = "KMS key for CloudTrail and SNS encryption"
  enable_key_rotation     = true
  deletion_window_in_days = var.kms_key_deletion_window

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudTrail and SNS"
        Effect = "Allow"
        Principal = {
          Service = [
            "cloudtrail.amazonaws.com",
            "sns.amazonaws.com"
          ]
        }
        Action = [
          "kms:GenerateDataKey*",
          "kms:Encrypt*",
          "kms:ReEncrypt*",
          "kms:Decrypt*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

# KMS key for S3 bucket encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for CloudTrail S3 bucket encryption"
  enable_key_rotation     = true
  deletion_window_in_days = var.kms_key_deletion_window

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

# S3 bucket for CloudTrail logs
resource "aws_s3_bucket" "cloudtrail" {
  bucket        = local.bucket_name
  force_destroy = false

  tags = local.common_tags

  lifecycle {
    prevent_destroy = false
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  rule {
    id     = "log-expiration"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = var.s3_lifecycle_expiration_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 EventBridge notification
resource "aws_s3_bucket_notification" "cloudtrail" {
  bucket      = aws_s3_bucket.cloudtrail.id
  eventbridge = true
}

# S3 access logging
resource "aws_s3_bucket_logging" "cloudtrail" {
  bucket        = aws_s3_bucket.cloudtrail.id
  target_bucket = aws_s3_bucket.cloudtrail.id
  target_prefix = "access-logs/"
}

# S3 bucket replication configuration
# Note: Replication is optional and requires a destination bucket and IAM role
# Uncomment and configure if cross-region replication is needed
# resource "aws_s3_bucket_replication_configuration" "cloudtrail" {
#   bucket = aws_s3_bucket.cloudtrail.id
#   role   = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/s3-replication-role"
#
#   rule {
#     id     = "replication-rule"
#     status = "Enabled"
#
#     delete_marker_replication {
#       status = "Disabled"
#     }
#
#     destination {
#       bucket        = "arn:aws:s3:::target-replication-bucket"
#       storage_class = "STANDARD"
#     }
#
#     filter {
#       prefix = ""
#     }
#   }
# }

# S3 bucket policy for CloudTrail
resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "cloudtrail" {
  name              = local.cloudwatch_log_name
  retention_in_days = 365 # Minimum 1 year retention for compliance (CKV_AWS_338)
  kms_key_id        = aws_kms_key.cloudwatch.arn

  tags = local.common_tags
}

# CloudWatch Log Stream
resource "aws_cloudwatch_log_stream" "cloudtrail" {
  name           = "${data.aws_caller_identity.current.account_id}_CloudTrail_${data.aws_region.current.name}"
  log_group_name = aws_cloudwatch_log_group.cloudtrail.name
}

# IAM policy for CloudTrail to write to CloudWatch
resource "aws_iam_policy" "cloudwatch" {
  name        = "${var.environment}-${local.service_name}-cloudwatch-policy"
  description = "Policy to enable CloudTrail logging into CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailCreateLogStream"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream"
        ]
        Resource = [
          "${aws_cloudwatch_log_stream.cloudtrail.arn}*"
        ]
      },
      {
        Sid    = "AWSCloudTrailPutLogEvents"
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents"
        ]
        Resource = [
          "${aws_cloudwatch_log_stream.cloudtrail.arn}*"
        ]
      }
    ]
  })

  tags = local.common_tags
}

# IAM role for CloudTrail to assume
resource "aws_iam_role" "cloudwatch" {
  name = "${var.environment}-${local.service_name}-cloudwatch-role"
  path = "/service-role/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.cloudwatch.name
  policy_arn = aws_iam_policy.cloudwatch.arn
}

# SNS topic for CloudTrail alerts
resource "aws_sns_topic" "cloudtrail" {
  name              = "${var.environment}-${local.service_name}-alerts"
  kms_master_key_id = aws_kms_key.cloudtrail.arn

  tags = local.common_tags
}

# SNS topic policy to allow CloudTrail to publish
resource "aws_sns_topic_policy" "cloudtrail" {
  arn = aws_sns_topic.cloudtrail.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailSNSPolicy"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.cloudtrail.arn
      }
    ]
  })
}

# CloudTrail trail
resource "aws_cloudtrail" "main" {
  name                       = "${var.environment}-${local.service_name}"
  s3_bucket_name             = aws_s3_bucket.cloudtrail.id
  is_multi_region_trail      = true
  enable_log_file_validation = true
  sns_topic_name             = aws_sns_topic.cloudtrail.name
  kms_key_id                 = aws_kms_key.cloudtrail.arn

  cloud_watch_logs_role_arn  = aws_iam_role.cloudwatch.arn
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.cloudtrail.arn}:*"

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    dynamic "data_resource" {
      for_each = var.enable_s3_data_events ? [1] : []
      content {
        type   = "AWS::S3::Object"
        values = ["arn:aws:s3"]
      }
    }
  }

  tags = local.common_tags

  depends_on = [
    aws_iam_role_policy_attachment.cloudwatch,
    aws_s3_bucket_policy.cloudtrail,
    aws_sns_topic_policy.cloudtrail
  ]
}
