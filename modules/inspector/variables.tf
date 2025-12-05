# Amazon Inspector Module - Variables

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "resource_types" {
  description = "Types of resources to scan (EC2, ECR, LAMBDA, LAMBDA_CODE)"
  type        = list(string)
  default     = ["EC2", "ECR", "LAMBDA"]

  validation {
    condition = alltrue([
      for rt in var.resource_types : contains(["EC2", "ECR", "LAMBDA", "LAMBDA_CODE"], rt)
    ])
    error_message = "Resource types must be one of: EC2, ECR, LAMBDA, LAMBDA_CODE."
  }
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
