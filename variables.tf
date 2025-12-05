# Root Module Variables

# Common Variables

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Module Enable Flags

variable "enable_cloudtrail" {
  description = "Enable CloudTrail module"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config module"
  type        = bool
  default     = true
}

variable "enable_guardduty" {
  description = "Enable GuardDuty module"
  type        = bool
  default     = true
}

variable "enable_detective" {
  description = "Enable Detective module"
  type        = bool
  default     = true
}

variable "enable_securityhub" {
  description = "Enable Security Hub module"
  type        = bool
  default     = true
}

# CloudTrail Module Variables

variable "cloudtrail_s3_lifecycle_expiration_days" {
  description = "Number of days before S3 objects expire in CloudTrail bucket"
  type        = number
  default     = 365
}

variable "cloudtrail_kms_key_deletion_window" {
  description = "Number of days before KMS key deletion for CloudTrail (7-30)"
  type        = number
  default     = 7
}

variable "cloudtrail_enable_s3_data_events" {
  description = "Enable S3 data events in CloudTrail"
  type        = bool
  default     = true
}

# AWS Config Module Variables

variable "config_s3_lifecycle_expiration_days" {
  description = "Number of days before S3 objects expire in Config bucket"
  type        = number
  default     = 365
}

variable "config_kms_key_deletion_window" {
  description = "Number of days before KMS key deletion for Config (7-30)"
  type        = number
  default     = 10
}

variable "config_include_global_resources" {
  description = "Include global resources in Config recording"
  type        = bool
  default     = true
}

# GuardDuty Module Variables

variable "guardduty_finding_publishing_frequency" {
  description = "Frequency of notifications about updated findings (FIFTEEN_MINUTES, ONE_HOUR, SIX_HOURS)"
  type        = string
  default     = "SIX_HOURS"
}

variable "guardduty_enable_s3_logs" {
  description = "Enable S3 protection data source in GuardDuty"
  type        = bool
  default     = true
}

variable "guardduty_enable_kubernetes_logs" {
  description = "Enable Kubernetes audit logs data source in GuardDuty"
  type        = bool
  default     = true
}

variable "guardduty_enable_malware_protection" {
  description = "Enable malware protection for EC2 instances in GuardDuty"
  type        = bool
  default     = true
}

variable "guardduty_auto_enable_organization_members" {
  description = "Auto-enable GuardDuty for organization members (ALL, NEW, NONE)"
  type        = string
  default     = "NEW"
}

variable "guardduty_is_organization_admin_account" {
  description = "Whether this account is the GuardDuty delegated administrator for the organization"
  type        = bool
  default     = false
}

# Security Hub Module Variables

variable "securityhub_enable_cis_standard" {
  description = "Enable CIS AWS Foundations Benchmark standard in Security Hub"
  type        = bool
  default     = true
}

variable "securityhub_enable_pci_dss_standard" {
  description = "Enable PCI DSS standard in Security Hub"
  type        = bool
  default     = false
}

variable "securityhub_enable_aws_foundational_standard" {
  description = "Enable AWS Foundational Security Best Practices standard in Security Hub"
  type        = bool
  default     = true
}