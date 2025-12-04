# GuardDuty Module Variables

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "finding_publishing_frequency" {
  description = "Frequency of notifications about updated findings (FIFTEEN_MINUTES, ONE_HOUR, SIX_HOURS)"
  type        = string
  default     = "SIX_HOURS"

  validation {
    condition     = contains(["FIFTEEN_MINUTES", "ONE_HOUR", "SIX_HOURS"], var.finding_publishing_frequency)
    error_message = "Finding publishing frequency must be FIFTEEN_MINUTES, ONE_HOUR, or SIX_HOURS."
  }
}

variable "enable_s3_logs" {
  description = "Enable S3 protection data source"
  type        = bool
  default     = true
}

variable "enable_kubernetes_logs" {
  description = "Enable Kubernetes audit logs data source"
  type        = bool
  default     = true
}

variable "enable_malware_protection" {
  description = "Enable malware protection for EC2 instances"
  type        = bool
  default     = true
}

variable "auto_enable_organization_members" {
  description = "Auto-enable GuardDuty for organization members (ALL, NEW, NONE)"
  type        = string
  default     = "NEW"

  validation {
    condition     = contains(["ALL", "NEW", "NONE"], var.auto_enable_organization_members)
    error_message = "Auto-enable organization members must be ALL, NEW, or NONE."
  }
}

variable "is_organization_admin_account" {
  description = "Whether this account is the GuardDuty delegated administrator for the organization"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
