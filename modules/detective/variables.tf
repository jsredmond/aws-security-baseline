# Detective Module Variables

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "is_organization_admin_account" {
  description = "Whether this account is the Detective delegated administrator for the organization"
  type        = bool
  default     = false
}

variable "auto_enable_organization_members" {
  description = "Whether to automatically enable Detective for new organization members"
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
