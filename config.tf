# KMS key for AWS Config
resource "aws_kms_key" "config_key" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

# Config bucket
resource "aws_s3_bucket" "config_bucket" {
  bucket        = "${var.env}-config-${random_id.random.dec}"
  force_destroy = true
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