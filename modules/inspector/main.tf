# Amazon Inspector Module - Main Resources
# This module enables Amazon Inspector for continuous vulnerability scanning

# Data sources for account ID
data "aws_caller_identity" "current" {}

# Enable Amazon Inspector for specified resource types
resource "aws_inspector2_enabler" "main" {
  account_ids    = [data.aws_caller_identity.current.account_id]
  resource_types = var.resource_types
}
