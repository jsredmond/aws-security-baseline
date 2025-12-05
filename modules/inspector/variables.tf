# Amazon Inspector Module - Variables
# Note: environment and common_tags are not used because aws_inspector2_enabler
# does not support tags

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
