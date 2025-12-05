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

# Detective Organization Configuration (conditional)
resource "aws_detective_organization_configuration" "main" {
  count = var.is_organization_admin_account ? 1 : 0

  graph_arn   = aws_detective_graph.main.graph_arn
  auto_enable = var.auto_enable_organization_members
}
