# Amazon Macie Module - Main Resources
# This module enables Amazon Macie for sensitive data discovery and protection

# Data sources for account ID
data "aws_caller_identity" "current" {}

# Enable Amazon Macie
resource "aws_macie2_account" "main" {
  finding_publishing_frequency = var.finding_publishing_frequency
  status                       = "ENABLED"
}
