# Environment Configuration
environment = "dev"
aws_region  = "us-east-1"

# Module Enable Flags
enable_cloudtrail  = true
enable_config      = true
enable_guardduty   = true
enable_detective   = false # Requires 48 hours of GuardDuty data
enable_securityhub = true

# CloudTrail Configuration
# Note: CloudWatch logs retention is hardcoded to 365 days for compliance
cloudtrail_s3_lifecycle_expiration_days = 365
cloudtrail_kms_key_deletion_window      = 7
cloudtrail_enable_s3_data_events        = true

# Config Configuration
config_s3_lifecycle_expiration_days = 365
config_kms_key_deletion_window      = 10
config_include_global_resources     = true

# GuardDuty Configuration
guardduty_finding_publishing_frequency     = "SIX_HOURS"
guardduty_enable_s3_logs                   = true
guardduty_enable_kubernetes_logs           = true
guardduty_enable_malware_protection        = true
guardduty_is_organization_admin_account    = false
guardduty_auto_enable_organization_members = "NEW"

# Security Hub Configuration
securityhub_enable_cis_standard              = true
securityhub_enable_pci_dss_standard          = false
securityhub_enable_aws_foundational_standard = true

# Common Tags
common_tags = {
  Project     = "AWS-Security-Baseline"
  ManagedBy   = "Terraform"
  Environment = "dev"
  Owner       = "Security-Team"
}
# IAM Access Analyzer Configuration
enable_accessanalyzer                 = true
accessanalyzer_is_organization        = false
accessanalyzer_enable_unused_access   = true
accessanalyzer_unused_access_age_days = 90

# Amazon Inspector Configuration
enable_inspector         = true
inspector_resource_types = ["EC2", "ECR", "LAMBDA"]

# Amazon Macie Configuration
enable_macie                       = true
macie_finding_publishing_frequency = "SIX_HOURS"
