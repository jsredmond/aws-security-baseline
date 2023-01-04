# Data call to get current AWS account and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# CloudTrail bucket name local
locals {
  cloudtrail_bucket_name = "${var.env}-cloudtrail-${random_id.random.dec}"
}

# KMS key to encrypt CloudWatch log group
resource "aws_kms_key" "cloudtrail_log_key" {
  description             = "This key is used to encrypt an eks cloudwatch log group"
  enable_key_rotation = true
  deletion_window_in_days = 7

  policy = <<EOF
{
  "Version" : "2012-10-17",
  "Id" : "key-default-1",
  "Statement" : [ {
      "Sid" : "Enable IAM User Permissions",
      "Effect" : "Allow",
      "Principal" : {
        "AWS" : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      },
      "Action" : "kms:*",
      "Resource" : "*"
    },
    {
      "Effect": "Allow",
      "Principal": { "Service": "logs.us-east-1.amazonaws.com" },
      "Action": [ 
        "kms:Encrypt*",
        "kms:Decrypt*",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:Describe*"
      ],
      "Resource": "*"
    }  
  ]
}
EOF
}

# CloudTrail KMS Policy
data "aws_iam_policy_document" "cloudtrail_kms" {
  statement {
    actions = [
      "kms:*",
    ]
    principals {
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
      ]
      type = "AWS"
    }
    resources = [
      "*",
    ]
    sid = "Enable IAM User Permissions"
  }

  statement {
    actions = [
      "kms:GenerateDataKey*",
    ]
    condition {
      test = "StringLike"
      values = [
        "arn:aws:cloudtrail:*:${data.aws_caller_identity.current.account_id}:trail/*",
      ]
      variable = "kms:EncryptionContext:aws:cloudtrail:arn"
    }
    principals {
      identifiers = [
        "cloudtrail.amazonaws.com",
      ]
      type = "Service"
    }
    resources = [
      "*",
    ]
    sid = "Allow CloudTrail to encrypt logs"
  }

  statement {
    actions = [
      "kms:DescribeKey",
    ]
    principals {
      identifiers = [
        "cloudtrail.amazonaws.com",
      ]
      type = "Service"
    }
    resources = [
      "*",
    ]
    sid = "Allow CloudTrail to describe key"
  }
}

# CloudTrail KMS Key
resource "aws_kms_key" "cloudtrail_kms_key" {
  description         = "cloudtrail log key"
  enable_key_rotation = true
  deletion_window_in_days = 7
  policy              = data.aws_iam_policy_document.cloudtrail_kms.json
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "cloudwatch_log_group" {
  name = "${var.env}_cloudwatch_log_group"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.cloudtrail_log_key.arn

  tags = {
    Name = "Cloudwatch for backuping CloudTrail"
    Environment = var.env
  }

}

# CloudWatch Log Stream
resource "aws_cloudwatch_log_stream" "cloudwatch_log_stream" {
  name           = "${data.aws_caller_identity.current.account_id}_CloudTrail_${data.aws_region.current.name}"
  log_group_name = aws_cloudwatch_log_group.cloudwatch_log_group.name
}

# CloudTrail logging into CloudWatch
resource "aws_iam_policy" "cloudtrail_cloudwatch_policy" {
  name        = "${var.env}_cloudtrail_cloudwatch_policy"
  description = "Policy to enable CloudTrail logging into CloudWatch on ${var.env}"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailCreateLogStream2014110${var.env}",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream"
      ],
      "Resource": [
        "${aws_cloudwatch_log_stream.cloudwatch_log_stream.arn}*"
      ]
    },
    {
      "Sid": "AWSCloudTrailPutLogEvents20141101${var.env}",
      "Effect": "Allow",
      "Action": [
        "logs:PutLogEvents"
      ],
      "Resource": [
        "${aws_cloudwatch_log_stream.cloudwatch_log_stream.arn}*"
      ]
    }
  ]
}
POLICY

  depends_on = [aws_cloudwatch_log_stream.cloudwatch_log_stream]
}

# CloudTrail Role
resource "aws_iam_role" "cloudtrail_cloudwatch_role" {
  name = "${var.env}_cloudtrail_cloudwatch_role"
  path = "/service-role/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

  tags = {
    Name = "IAM Role for CloudTrail logging into CloudWatch"
    Environment = var.env
  }

  depends_on = [aws_iam_policy.cloudtrail_cloudwatch_policy]
}

# CloudTrail Role Policy Assignment
resource "aws_iam_role_policy_attachment" "cloudtrail_cloudwatch_role_policy_attachement" {
  role       = aws_iam_role.cloudtrail_cloudwatch_role.name
  policy_arn = aws_iam_policy.cloudtrail_cloudwatch_policy.arn

  depends_on = [aws_iam_role.cloudtrail_cloudwatch_role]
}

# CloudTrail Bucket
resource "aws_s3_bucket" "cloudtrail_bucket" {
  bucket = local.cloudtrail_bucket_name
  force_destroy = true
  tags = {
    Name = "Bucket for logs"
    Environment = var.env
  }
}

# CloudTrail bucket policy
resource "aws_s3_bucket_policy" "cloudtrail_bucket_policy" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::${local.cloudtrail_bucket_name}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${local.cloudtrail_bucket_name}/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
POLICY
}

# CloudTrail Bucket Prevent Public Access
resource "aws_s3_bucket_public_access_block" "s3_cloudtrail_bucket_public_access" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id

  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

# Enable CloudTrail
resource "aws_cloudtrail" "cloudtrail" {
  name = "${var.env}_cloudtrail"
  s3_bucket_name = aws_s3_bucket.cloudtrail_bucket.id
  is_multi_region_trail = true
  enable_log_file_validation = true
  kms_key_id = aws_kms_key.cloudtrail_kms_key.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = false

    data_resource {
      type = "AWS::S3::Object"

      values = ["arn:aws:s3"]

    }
  }

  tags = {
    Name = "CloudTrail events"
    Environment = var.env
  }

  cloud_watch_logs_role_arn = aws_iam_role.cloudtrail_cloudwatch_role.arn
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.cloudwatch_log_group.arn}:*"

  depends_on = [
    aws_iam_role_policy_attachment.cloudtrail_cloudwatch_role_policy_attachement,
    aws_s3_bucket.cloudtrail_bucket
  ]
}

# CloudTrail KMS Key
resource "aws_kms_key" "cloudtrail_key" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

# Encrypt CloudTrail Bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "encrypt_cloudtrail_bucket" {
  bucket = aws_s3_bucket.cloudtrail_bucket.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.cloudtrail_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# CloudTrail Bucket Versioning
resource "aws_s3_bucket_versioning" "version_cloudtrail_bucket" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id
  versioning_configuration {
    status     = "Enabled"
  }
}