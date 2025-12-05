# Amazon Macie Module - Main Resources
# This module enables Amazon Macie for sensitive data discovery and protection

# Data sources for account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random ID for unique naming
resource "random_id" "suffix" {
  byte_length = 8
}

# Locals for computed values
locals {
  service_name = "macie"

  common_tags = merge(
    var.common_tags,
    {
      Name        = "${var.environment}-${local.service_name}"
      Environment = var.environment
      Module      = local.service_name
      ManagedBy   = "Terraform"
    }
  )
}

# Enable Amazon Macie
resource "aws_macie2_account" "main" {
  finding_publishing_frequency = var.finding_publishing_frequency
  status                       = "ENABLED"
}
