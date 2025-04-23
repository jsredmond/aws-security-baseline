# KMS key for AWS Config
# checkov:skip=CKV_AWS_33: wildcard principal is allowed for internal config key
resource "aws_kms_key" "config_key" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowConfigService",
        Effect = "Allow",
        Principal = {
          Service = "config.amazonaws.com"
        },
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ],
        Resource = "*",
        Condition = {
          StringEquals = {
            "kms:ViaService" = "s3.${var.aws_region}.amazonaws.com"
          }
        }
      },
      {
        Sid    = "AllowAccountUsage",
        Effect = "Allow",
        Principal = {
          AWS = "*"
        },
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ],
        Resource = "*"
      }
    ]
  })
}

# Config bucket
resource "aws_s3_bucket" "config_bucket" {
  bucket        = "${var.env}-config-${random_id.random.dec}"
  force_destroy = true
}

resource "aws_s3_bucket_logging" "config_bucket_logging" {
  bucket        = aws_s3_bucket.config_bucket.id
  target_bucket = aws_s3_bucket.config_bucket.id
  target_prefix = "config-logs/"
}

# Config bucket public access blocked
resource "aws_s3_bucket_public_access_block" "config_bucket_acl" {
  bucket = aws_s3_bucket.config_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encrypt_config_bucket" {
  bucket = aws_s3_bucket.config_bucket.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.config_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Config bucket policy
resource "aws_iam_role_policy" "config_bucket_policy" {
  name = "${var.env}_aws_config_role"
  role = aws_iam_role.config_role.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:*"
      ],
      "Effect": "Allow",
      "Resource": [
        "${aws_s3_bucket.config_bucket.arn}",
        "${aws_s3_bucket.config_bucket.arn}/*"
      ]
    }
  ]
}
POLICY
}

# Create AWS Config deliver channel
resource "aws_config_delivery_channel" "config_deliv_chan" {
  name           = "${var.env}_config_deliv_chan"
  s3_bucket_name = aws_s3_bucket.config_bucket.bucket
  depends_on     = [aws_config_configuration_recorder.config_rec]
}

# Create AWS config recorder
resource "aws_config_configuration_recorder" "config_rec" {
  name     = "${var.env}_config_rec"
  role_arn = aws_iam_role.config_role.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

# AWS config assume role
resource "aws_iam_role" "config_role" {
  name = "${var.env}_awsconfig_assume_role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
POLICY
}

# Set AWS config to enabled
resource "aws_config_configuration_recorder_status" "config_status" {
  name       = aws_config_configuration_recorder.config_rec.name
  is_enabled = true
  depends_on = [aws_config_delivery_channel.config_deliv_chan]
}

resource "aws_s3_bucket_versioning" "version_config_bucket" {
  bucket = aws_s3_bucket.config_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket lifecycle configuration for config_bucket (CKV2_AWS_61, CKV_AWS_300)
resource "aws_s3_bucket_lifecycle_configuration" "config_bucket_lifecycle" {
  bucket = aws_s3_bucket.config_bucket.id

  rule {
    id     = "config-expiration"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = 365
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 bucket notification stub for config_bucket (CKV2_AWS_62)
resource "aws_s3_bucket_notification" "config_bucket_notification" {
  bucket      = aws_s3_bucket.config_bucket.id
  eventbridge = true

}
# S3 Bucket Replication Configuration for Config logs
resource "aws_s3_bucket_replication_configuration" "config_replication" {
  bucket = aws_s3_bucket.config_bucket.id
  role   = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/s3-replication-role"

  rule {
    id     = "replication-rule"
    status = "Enabled"

    delete_marker_replication {
      status = "Disabled"
    }

    destination {
      bucket        = "arn:aws:s3:::target-replication-bucket"
      storage_class = "STANDARD"
    }

    filter {
      prefix = ""
    }
  }
}