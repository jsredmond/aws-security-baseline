# Environment Configuration
environment = "dev"
aws_region  = "us-east-1"

# Module Enable Flags
enable_cloudtrail   = true
enable_config       = true
enable_guardduty    = true
enable_detective    = false  # Requires 48 hours of GuardDuty data
enable_securityhub  = true

# CloudTrail Configuration
cloudtrail_cloudwatch_logs_retention_days = 90
cloudtrail_s3_lifecycle_expiration_days   = 365
cloudtrail_kms_key_deletion_window        = 7
cloudtrail_enable_s3_data_events          = true

# Config Configuration
config_s3_lifecycle_expiration_days = 365
config_kms_key_deletion_window      = 10
config_include_global_resources     = true

# GuardDuty Configuration
guardduty_finding_publishing_frequency    = "SIX_HOURS"
guardduty_enable_s3_logs                  = true
guardduty_enable_kubernetes_logs          = true
guardduty_enable_malware_protection       = true
guardduty_is_organization_admin_account   = false
guardduty_auto_enable_organization_members = "NEW"

# Security Hub Configuration
securityhub_enable_cis_standard                = true
securityhub_enable_pci_dss_standard            = false
securityhub_enable_aws_foundational_standard   = true

# Common Tags
common_tags = {
  Project     = "AWS-Security-Baseline"
  ManagedBy   = "Terraform"
  Environment = "dev"
  Owner       = "Security-Team"
}
