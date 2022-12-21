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