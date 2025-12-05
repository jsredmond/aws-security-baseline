# IAM Access Analyzer Module - Variables

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "is_organization_analyzer" {
  description = "Whether to create an organization-level analyzer (requires AWS Organizations)"
  type        = bool
  default     = false
}

variable "enable_unused_access_analyzer" {
  description = "Enable unused access analyzer to identify unused IAM permissions (Note: ACCOUNT_UNUSED_ACCESS type may not be supported in all regions/versions)"
  type        = bool
  default     = false
}

variable "unused_access_age_days" {
  description = "Number of days to consider access as unused"
  type        = number
  default     = 90

  validation {
    condition     = var.unused_access_age_days >= 1 && var.unused_access_age_days <= 365
    error_message = "Unused access age must be between 1 and 365 days."
  }
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
