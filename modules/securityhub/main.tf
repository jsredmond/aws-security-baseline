# Data sources
data "aws_region" "current" {}

# Locals for computed values
locals {
  # Map of standards to enable
  enabled_standards_map = {
    cis = var.enable_cis_standard ? "arn:aws:securityhub:${data.aws_region.current.id}::standards/cis-aws-foundations-benchmark/v/1.4.0" : null
    pci = var.enable_pci_dss_standard ? "arn:aws:securityhub:${data.aws_region.current.id}::standards/pci-dss/v/3.2.1" : null
    aws = var.enable_aws_foundational_standard ? "arn:aws:securityhub:${data.aws_region.current.id}::standards/aws-foundational-security-best-practices/v/1.0.0" : null
  }

  # Filter out null values
  enabled_standards = { for k, v in local.enabled_standards_map : k => v if v != null }
}

# Enable Security Hub
resource "aws_securityhub_account" "main" {
  enable_default_standards  = false
  control_finding_generator = "SECURITY_CONTROL"
  auto_enable_controls      = true
}

# Subscribe to security standards
resource "aws_securityhub_standards_subscription" "standards" {
  for_each = local.enabled_standards

  standards_arn = each.value

  depends_on = [aws_securityhub_account.main]
}

# GuardDuty product integration
resource "aws_securityhub_product_subscription" "guardduty" {
  count = var.enable_guardduty_integration ? 1 : 0

  product_arn = "arn:aws:securityhub:${data.aws_region.current.id}::product/aws/guardduty"

  depends_on = [aws_securityhub_account.main]
}

# Inspector product integration
resource "aws_securityhub_product_subscription" "inspector" {
  count = var.enable_inspector_integration ? 1 : 0

  product_arn = "arn:aws:securityhub:${data.aws_region.current.id}::product/aws/inspector"

  depends_on = [aws_securityhub_account.main]
}

# Macie product integration
resource "aws_securityhub_product_subscription" "macie" {
  count = var.enable_macie_integration ? 1 : 0

  product_arn = "arn:aws:securityhub:${data.aws_region.current.id}::product/aws/macie"

  depends_on = [aws_securityhub_account.main]
}
