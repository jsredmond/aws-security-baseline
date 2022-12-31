# Used to call the AWS account ID
data "aws_caller_identity" "current" {}

# CloudTrail bucket
resource "aws_s3_bucket" "ct-bucket" {
  bucket        = "${var.env}-cloudtrail-${random_id.random.dec}"
  force_destroy = true
}

# CloudTrail bucket public access blocked
resource "aws_s3_bucket_public_access_block" "ct-bucket-acl" {
  bucket = aws_s3_bucket.ct-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# resource "aws_s3_bucket_versioning" "version-ct-bucket" {
#   bucket = aws_s3_bucket.ct-bucket.id
#   versioning_configuration {
#     status     = "Enabled"
#     mfa_delete = "Enabled"
#   }
# }

resource "aws_kms_key" "s3key" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encrypt-ct-bucket" {
  bucket = aws_s3_bucket.ct-bucket.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# CloudTrail bucket policy
resource "aws_s3_bucket_policy" "ct-bucket-policy" {
  bucket = aws_s3_bucket.ct-bucket.id
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
            "Resource": "${aws_s3_bucket.ct-bucket.arn}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "${aws_s3_bucket.ct-bucket.arn}/prefix/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
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

# KMS key to encrypt CloudWatch log group
resource "aws_kms_key" "ctkey" {
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

# Create CloudWatch log group for CloudTrail
resource "aws_cloudwatch_log_group" "cloudwatch-ct-logs" {
  name              = "cloudwatch-ct-logs"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.ctkey.arn
}

resource "aws_iam_role" "cloudtrail_role" {
  name               = "cloudtrail_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "cloudtrail_policy" {
  name        = "cloudtrail_policy"
  description = "Policy for CloudTrail to write to CloudWatch Logs group"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect": "Allow",
      "Resource": "${aws_cloudwatch_log_group.cloudwatch-ct-logs.arn}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "cloudtrail_policy_attachment" {
  role       = aws_iam_role.cloudtrail_role.name
  policy_arn = aws_iam_policy.cloudtrail_policy.arn
}


# Enabling CloudTrail
resource "aws_cloudtrail" "cloudtrail" {
  name                          = "${var.env}-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.ct-bucket.bucket
  s3_key_prefix                 = "prefix"
  include_global_service_events = true
  enable_log_file_validation    = true
  is_multi_region_trail         = true
  kms_key_id                    = aws_kms_key.ctkey.arn
  cloud_watch_logs_group_arn    = "${aws_cloudwatch_log_group.cloudwatch-ct-logs.arn}:*"
  cloud_watch_logs_role_arn     = "${aws_iam_role.cloudtrail_role.arn}"
}
