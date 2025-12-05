# AWS Config Module - Main Resources

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random ID for unique bucket naming
resource "random_id" "suffix" {
  byte_length = 8
}

# Locals for computed values
locals {
  service_name = "config"
  bucket_name  = "${var.environment}-${local.service_name}-${random_id.suffix.dec}"
  account_id   = data.aws_caller_identity.current.account_id
  region       = data.aws_region.current.name

  common_tags = merge(
    var.common_tags,
    {
      Name        = "${var.environment}-${local.service_name}"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = local.service_name
    }
  )
}

# KMS key for AWS Config encryption
resource "aws_kms_key" "config" {
  description             = "KMS key for AWS Config encryption"
  deletion_window_in_days = var.kms_key_deletion_window
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowConfigService"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "s3.${local.region}.amazonaws.com"
          }
        }
      },
      {
        Sid    = "AllowAccountUsage"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = [
              "s3.${local.region}.amazonaws.com",
              "config.${local.region}.amazonaws.com"
            ]
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_kms_alias" "config" {
  name          = "alias/${var.environment}-${local.service_name}"
  target_key_id = aws_kms_key.config.key_id
}

# S3 bucket for Config
resource "aws_s3_bucket" "config" {
  bucket        = local.bucket_name
  force_destroy = false

  tags = local.common_tags
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "config" {
  bucket = aws_s3_bucket.config.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "config" {
  bucket = aws_s3_bucket.config.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.config.arn
    }
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "config" {
  bucket = aws_s3_bucket.config.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "config" {
  bucket = aws_s3_bucket.config.id

  rule {
    id     = "config-expiration"
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

# S3 bucket logging
resource "aws_s3_bucket_logging" "config" {
  bucket        = aws_s3_bucket.config.id
  target_bucket = aws_s3_bucket.config.id
  target_prefix = "config-logs/"
}

# S3 bucket notification
resource "aws_s3_bucket_notification" "config" {
  bucket      = aws_s3_bucket.config.id
  eventbridge = true
}

# S3 bucket policy for AWS Config service
resource "aws_s3_bucket_policy" "config" {
  bucket = aws_s3_bucket.config.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSConfigBucketPermissionsCheck"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.config.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      },
      {
        Sid    = "AWSConfigBucketExistenceCheck"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:ListBucket"
        Resource = aws_s3_bucket.config.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      },
      {
        Sid    = "AWSConfigBucketDelivery"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.config.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl"      = "bucket-owner-full-control"
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# S3 bucket replication configuration
# Note: Replication is optional and requires a destination bucket and IAM role
# Uncomment and configure if cross-region replication is needed
# resource "aws_s3_bucket_replication_configuration" "config" {
#   bucket = aws_s3_bucket.config.id
#   role   = "arn:aws:iam::${local.account_id}:role/s3-replication-role"
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

# IAM role for AWS Config
resource "aws_iam_role" "config" {
  name = "${var.environment}-${local.service_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = ""
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

# IAM role policy for S3 bucket access
resource "aws_iam_role_policy" "config_bucket" {
  name = "${var.environment}-${local.service_name}-bucket-policy"
  role = aws_iam_role.config.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSConfigBucketPermissions"
        Effect = "Allow"
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketLocation"
        ]
        Resource = aws_s3_bucket.config.arn
      },
      {
        Sid    = "AWSConfigObjectPermissions"
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.config.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# Attach AWS managed policy for Config service
resource "aws_iam_role_policy_attachment" "config_policy" {
  role       = aws_iam_role.config.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}

# AWS Config configuration recorder
resource "aws_config_configuration_recorder" "main" {
  name     = "${var.environment}-${local.service_name}-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = var.include_global_resources
  }
}

# AWS Config delivery channel
resource "aws_config_delivery_channel" "main" {
  name           = "${var.environment}-${local.service_name}-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config.id

  depends_on = [aws_config_configuration_recorder.main]
}

# Enable AWS Config recorder
resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true

  depends_on = [aws_config_delivery_channel.main]
}
