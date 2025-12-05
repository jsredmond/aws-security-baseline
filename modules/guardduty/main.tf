# GuardDuty Module - Threat Detection Service
# This module deploys and configures Amazon GuardDuty with organization-wide threat detection

# Random ID for unique naming
resource "random_id" "suffix" {
  byte_length = 8
}

# Locals for computed values
locals {
  service_name = "guardduty"
  common_tags = merge(
    var.common_tags,
    {
      Name        = "${var.environment}-${local.service_name}"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Module      = local.service_name
    }
  )
}

# GuardDuty Detector
resource "aws_guardduty_detector" "main" {
  enable                       = true
  finding_publishing_frequency = var.finding_publishing_frequency

  datasources {
    s3_logs {
      enable = var.enable_s3_logs
    }
    kubernetes {
      audit_logs {
        enable = var.enable_kubernetes_logs
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = var.enable_malware_protection
        }
      }
    }
  }

  tags = local.common_tags
}

# GuardDuty Runtime Monitoring (EC2, EKS, ECS Fargate)
resource "aws_guardduty_detector_feature" "runtime_monitoring" {
  detector_id = aws_guardduty_detector.main.id
  name        = "RUNTIME_MONITORING"
  status      = "ENABLED"

  additional_configuration {
    name   = "EKS_ADDON_MANAGEMENT"
    status = "ENABLED"
  }

  additional_configuration {
    name   = "ECS_FARGATE_AGENT_MANAGEMENT"
    status = "ENABLED"
  }

  additional_configuration {
    name   = "EC2_AGENT_MANAGEMENT"
    status = "ENABLED"
  }
}

# GuardDuty Lambda Protection
resource "aws_guardduty_detector_feature" "lambda_protection" {
  detector_id = aws_guardduty_detector.main.id
  name        = "LAMBDA_NETWORK_LOGS"
  status      = "ENABLED"
}

# GuardDuty RDS Protection
resource "aws_guardduty_detector_feature" "rds_protection" {
  detector_id = aws_guardduty_detector.main.id
  name        = "RDS_LOGIN_EVENTS"
  status      = "ENABLED"
}

# GuardDuty EKS Runtime Monitoring
resource "aws_guardduty_detector_feature" "eks_runtime_monitoring" {
  detector_id = aws_guardduty_detector.main.id
  name        = "EKS_RUNTIME_MONITORING"
  status      = "ENABLED"

  additional_configuration {
    name   = "EKS_ADDON_MANAGEMENT"
    status = "ENABLED"
  }
}

# GuardDuty Organization Configuration (conditional)
resource "aws_guardduty_organization_configuration" "main" {
  count = var.is_organization_admin_account ? 1 : 0

  detector_id                      = aws_guardduty_detector.main.id
  auto_enable_organization_members = var.auto_enable_organization_members

  datasources {
    s3_logs {
      auto_enable = var.enable_s3_logs
    }
    kubernetes {
      audit_logs {
        enable = var.enable_kubernetes_logs
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          auto_enable = var.enable_malware_protection
        }
      }
    }
  }
}
