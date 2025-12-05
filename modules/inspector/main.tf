# Amazon Inspector Module - Main Resources
# This module enables Amazon Inspector for continuous vulnerability scanning

# Data sources for account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random ID for unique naming
resource "random_id" "suffix" {
  byte_length = 8
}

# Locals for computed values
locals {
  service_name = "inspector"

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

# Enable Amazon Inspector for specified resource types
resource "aws_inspector2_enabler" "main" {
  account_ids    = [data.aws_caller_identity.current.account_id]
  resource_types = var.resource_types
}
