resource "aws_guardduty_detector" "detector" {
  enable = true
}

# resource "aws_guardduty_organization_configuration" "detectororg" {
#   auto_enable_organization_members = "ALL"

#   detector_id = aws_guardduty_detector.detector.id

#   datasources {
#     s3_logs {
#       auto_enable = true
#     }
#     kubernetes {
#       audit_logs {
#         enable = true
#       }
#     }
#     malware_protection {
#       scan_ec2_instance_with_findings {
#         ebs_volumes {
#           auto_enable = true
#         }
#       }
#     }
#   }
# }