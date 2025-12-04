# GuardDuty Module Outputs

output "detector_id" {
  description = "The ID of the GuardDuty detector"
  value       = aws_guardduty_detector.main.id
}

output "detector_arn" {
  description = "The ARN of the GuardDuty detector"
  value       = aws_guardduty_detector.main.arn
}

output "account_id" {
  description = "The AWS account ID where GuardDuty is enabled"
  value       = aws_guardduty_detector.main.account_id
}
