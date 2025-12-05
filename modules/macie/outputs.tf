# Amazon Macie Module - Outputs

output "macie_account_id" {
  description = "The unique identifier for the Macie account"
  value       = aws_macie2_account.main.id
}

output "service_role_arn" {
  description = "ARN of the service-linked role for Macie"
  value       = aws_macie2_account.main.service_role
}

output "created_at" {
  description = "Timestamp when Macie was enabled"
  value       = aws_macie2_account.main.created_at
}

output "account_id" {
  description = "AWS account ID where Macie is enabled"
  value       = data.aws_caller_identity.current.account_id
}
