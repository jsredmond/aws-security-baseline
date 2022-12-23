# CloudTrail bucket
resource "aws_s3_bucket" "ct-bucket" {
  bucket        = "${var.prefix_name}-cloudtrail-${random_id.my-random-id.dec}"
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

# Config bucket
resource "aws_s3_bucket" "config-bucket" {
  bucket        = "${var.prefix_name}-config-${random_id.my-random-id.dec}"
  force_destroy = true
}

# Config bucket public access blocked
resource "aws_s3_bucket_public_access_block" "config-bucket-acl" {
  bucket = aws_s3_bucket.config-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encrypt-config-bucket" {
  bucket = aws_s3_bucket.config-bucket.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Config bucket policy
resource "aws_iam_role_policy" "config-bucket-policy" {
  name = "${var.prefix_name}-awsconfig-role"
  role = aws_iam_role.configrole.id

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
        "${aws_s3_bucket.config-bucket.arn}",
        "${aws_s3_bucket.config-bucket.arn}/*"
      ]
    }
  ]
}
POLICY
}