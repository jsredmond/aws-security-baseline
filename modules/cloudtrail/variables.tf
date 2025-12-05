# CloudTrail Module - Input Variables

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "s3_lifecycle_expiration_days" {
  description = "Number of days before S3 objects expire"
  type        = number
  default     = 365

  validation {
    condition     = var.s3_lifecycle_expiration_days > 0
    error_message = "S3 lifecycle expiration days must be greater than 0."
  }
}

variable "kms_key_deletion_window" {
  description = "Number of days before KMS key deletion (7-30)"
  type        = number
  default     = 7

  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "KMS key deletion window must be between 7 and 30 days."
  }
}

variable "enable_s3_data_events" {
  description = "Enable S3 data events in CloudTrail"
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
