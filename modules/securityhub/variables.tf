variable "enable_cis_standard" {
  description = "Enable CIS AWS Foundations Benchmark standard"
  type        = bool
  default     = true
}

variable "enable_pci_dss_standard" {
  description = "Enable PCI DSS standard"
  type        = bool
  default     = false
}

variable "enable_aws_foundational_standard" {
  description = "Enable AWS Foundational Security Best Practices standard"
  type        = bool
  default     = true
}
