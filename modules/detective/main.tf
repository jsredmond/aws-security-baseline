# Detective Module - Security Investigation Service
# This module deploys and configures Amazon Detective for security investigation

# Random ID for unique naming
resource "random_id" "suffix" {
  byte_length = 8
}

# Locals for computed values
locals {
  service_name = "detective"
  common_tags = merge(
    var.common_tags,
    {
      Name        = "${var.environment}-${local.service_name}"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = local.service_name
    }
  )
}

# Detective Graph
resource "aws_detective_graph" "main" {
  tags = local.common_tags
}
