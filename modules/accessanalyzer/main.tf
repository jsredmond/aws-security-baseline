# IAM Access Analyzer Module - Main Resources
# This module deploys AWS IAM Access Analyzer for identifying external access to resources

# Data sources for account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random ID for unique naming
resource "random_id" "suffix" {
  byte_length = 8
}

# Locals for computed values
locals {
  service_name = "accessanalyzer"

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

# IAM Access Analyzer - External Access
resource "aws_accessanalyzer_analyzer" "external" {
  analyzer_name = "${var.environment}-external-access-analyzer"
  type          = var.is_organization_analyzer ? "ORGANIZATION" : "ACCOUNT"

  tags = local.common_tags
}

# IAM Access Analyzer - Unused Access (optional)
resource "aws_accessanalyzer_analyzer" "unused" {
  count = var.enable_unused_access_analyzer ? 1 : 0

  analyzer_name = "${var.environment}-unused-access-analyzer"
  type          = var.is_organization_analyzer ? "ORGANIZATION_UNUSED_ACCESS" : "ACCOUNT_UNUSED_ACCESS"

  configuration {
    unused_access {
      unused_access_age = var.unused_access_age_days
    }
  }

  tags = local.common_tags
}
