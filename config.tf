# Create AWS Config deliver channel
resource "aws_config_delivery_channel" "my-config-deliv-chan" {
  name           = "${var.prefix_name}-config-deliv-chan"
  s3_bucket_name = aws_s3_bucket.config-bucket.bucket
  depends_on     = [aws_config_configuration_recorder.my-config-rec]
}

# Create AWS config recorder
resource "aws_config_configuration_recorder" "my-config-rec" {
  name     = "${var.prefix_name}-config-rec"
  role_arn = aws_iam_role.configrole.arn
}

# AWS config assume role
resource "aws_iam_role" "configrole" {
  name = "${var.prefix_name}-awsconfig-assume-role"

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
resource "aws_config_configuration_recorder_status" "my-config-status" {
  name       = aws_config_configuration_recorder.my-config-rec.name
  is_enabled = true
  depends_on = [aws_config_delivery_channel.my-config-deliv-chan]
}