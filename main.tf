# Root Module - AWS Security Baseline
# This module orchestrates the deployment of AWS security services

# CloudTrail Module
module "cloudtrail" {
  count  = var.enable_cloudtrail ? 1 : 0
  source = "./modules/cloudtrail"

  environment                  = var.environment
  s3_lifecycle_expiration_days = var.cloudtrail_s3_lifecycle_expiration_days
  kms_key_deletion_window      = var.cloudtrail_kms_key_deletion_window
  enable_s3_data_events        = var.cloudtrail_enable_s3_data_events
  common_tags                  = var.common_tags
}

# AWS Config Module
module "config" {
  count  = var.enable_config ? 1 : 0
  source = "./modules/config"

  environment                  = var.environment
  s3_lifecycle_expiration_days = var.config_s3_lifecycle_expiration_days
  kms_key_deletion_window      = var.config_kms_key_deletion_window
  include_global_resources     = var.config_include_global_resources
  common_tags                  = var.common_tags
}

# GuardDuty Module
module "guardduty" {
  count  = var.enable_guardduty ? 1 : 0
  source = "./modules/guardduty"

  environment                      = var.environment
  finding_publishing_frequency     = var.guardduty_finding_publishing_frequency
  enable_s3_logs                   = var.guardduty_enable_s3_logs
  enable_kubernetes_logs           = var.guardduty_enable_kubernetes_logs
  enable_malware_protection        = var.guardduty_enable_malware_protection
  auto_enable_organization_members = var.guardduty_auto_enable_organization_members
  is_organization_admin_account    = var.guardduty_is_organization_admin_account
  common_tags                      = var.common_tags
}

# Detective Module
module "detective" {
  count  = var.enable_detective ? 1 : 0
  source = "./modules/detective"

  environment = var.environment
  common_tags = var.common_tags
}

# Security Hub Module
module "securityhub" {
  count  = var.enable_securityhub ? 1 : 0
  source = "./modules/securityhub"

  enable_cis_standard              = var.securityhub_enable_cis_standard
  enable_pci_dss_standard          = var.securityhub_enable_pci_dss_standard
  enable_aws_foundational_standard = var.securityhub_enable_aws_foundational_standard
}

# IAM Access Analyzer Module
module "accessanalyzer" {
  count  = var.enable_accessanalyzer ? 1 : 0
  source = "./modules/accessanalyzer"

  environment                   = var.environment
  is_organization_analyzer      = var.accessanalyzer_is_organization
  enable_unused_access_analyzer = var.accessanalyzer_enable_unused_access
  unused_access_age_days        = var.accessanalyzer_unused_access_age_days
  common_tags                   = var.common_tags
}

# Amazon Inspector Module
module "inspector" {
  count  = var.enable_inspector ? 1 : 0
  source = "./modules/inspector"

  resource_types = var.inspector_resource_types
}

# Amazon Macie Module
module "macie" {
  count  = var.enable_macie ? 1 : 0
  source = "./modules/macie"

  finding_publishing_frequency = var.macie_finding_publishing_frequency
}
