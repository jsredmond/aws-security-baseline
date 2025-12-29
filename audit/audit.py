#!/usr/bin/env python3
"""
AWS Security Baseline Audit Script

This script audits AWS security service modules against best practices using
MCP servers for AWS documentation and Terraform resource schemas.
"""

import json
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    """Finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    """Finding categories"""
    ENCRYPTION = "encryption"
    ACCESS_CONTROL = "access_control"
    LOGGING = "logging"
    MONITORING = "monitoring"
    COMPLIANCE = "compliance"
    CONFIGURATION = "configuration"


@dataclass
class Finding:
    """Represents a single audit finding"""
    module: str
    resource: str
    severity: Severity
    category: Category
    title: str
    description: str
    current_config: str
    recommended_config: str
    aws_doc_reference: str
    terraform_doc_reference: str
    breaking_change: bool
    effort: str  # "low" | "medium" | "high"

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        result = asdict(self)
        result['severity'] = self.severity.value
        result['category'] = self.category.value
        return result


@dataclass
class AuditSummary:
    """Summary statistics for audit report"""
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
    modules_audited: List[str]


class AuditReport:
    """Manages audit findings and report generation"""
    
    def __init__(self):
        self.findings: List[Finding] = []
        self.timestamp: str = ""
    
    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the report"""
        self.findings.append(finding)
    
    def get_summary(self) -> AuditSummary:
        """Generate summary statistics"""
        severity_counts = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0
        }
        
        modules = set()
        
        for finding in self.findings:
            severity_counts[finding.severity] += 1
            modules.add(finding.module)
        
        return AuditSummary(
            total_findings=len(self.findings),
            critical=severity_counts[Severity.CRITICAL],
            high=severity_counts[Severity.HIGH],
            medium=severity_counts[Severity.MEDIUM],
            low=severity_counts[Severity.LOW],
            modules_audited=sorted(list(modules))
        )
    
    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        """Get all findings of a specific severity"""
        return [f for f in self.findings if f.severity == severity]
    
    def get_findings_by_module(self, module: str) -> List[Finding]:
        """Get all findings for a specific module"""
        return [f for f in self.findings if f.module == module]
    
    def get_quick_wins(self) -> List[Finding]:
        """Get findings that are low effort but provide security value"""
        return [f for f in self.findings 
                if f.effort == "low" and f.severity in [Severity.HIGH, Severity.MEDIUM]]
    
    def generate_markdown_report(self, output_path: str) -> None:
        """Generate a comprehensive markdown audit report"""
        from datetime import datetime
        
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = self.get_summary()
        
        with open(output_path, 'w') as f:
            # Header
            f.write("# AWS Security Baseline Audit Report\n\n")
            f.write(f"**Generated:** {self.timestamp}\n\n")
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Findings:** {summary.total_findings}\n")
            f.write(f"- **Critical:** {summary.critical}\n")
            f.write(f"- **High:** {summary.high}\n")
            f.write(f"- **Medium:** {summary.medium}\n")
            f.write(f"- **Low:** {summary.low}\n")
            f.write(f"- **Modules Audited:** {', '.join(summary.modules_audited)}\n")
            
            quick_wins = self.get_quick_wins()
            f.write(f"- **Quick Wins Identified:** {len(quick_wins)}\n\n")
            
            # Table of Contents
            f.write("## Table of Contents\n\n")
            f.write("1. [Executive Summary](#executive-summary)\n")
            f.write("2. [Findings by Module](#findings-by-module)\n")
            for module in summary.modules_audited:
                f.write(f"   - [{module.title()}](#module-{module})\n")
            f.write("3. [Quick Wins](#quick-wins)\n")
            f.write("4. [Recommendations](#recommendations)\n")
            f.write("5. [References](#references)\n\n")
            f.write("---\n\n")
            
            # Findings by Module
            f.write("## Findings by Module\n\n")
            
            for module in summary.modules_audited:
                f.write(f"### Module: {module.title()}\n\n")
                module_findings = self.get_findings_by_module(module)
                
                # Group by severity
                for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                    severity_findings = [f for f in module_findings if f.severity == severity]
                    if severity_findings:
                        f.write(f"#### {severity.value.title()} Severity\n\n")
                        
                        for finding in severity_findings:
                            f.write(f"##### {finding.title}\n\n")
                            f.write(f"**Resource:** `{finding.resource}`\n\n")
                            f.write(f"**Category:** {finding.category.value.replace('_', ' ').title()}\n\n")
                            f.write(f"**Effort:** {finding.effort.title()}\n\n")
                            f.write(f"**Breaking Change:** {'Yes' if finding.breaking_change else 'No'}\n\n")
                            
                            f.write("**Description:**\n\n")
                            f.write(f"{finding.description}\n\n")
                            
                            f.write("**Current Configuration:**\n\n")
                            f.write("```hcl\n")
                            f.write(finding.current_config)
                            f.write("\n```\n\n")
                            
                            f.write("**Recommended Configuration:**\n\n")
                            f.write("```hcl\n")
                            f.write(finding.recommended_config)
                            f.write("\n```\n\n")
                            
                            f.write("**References:**\n\n")
                            f.write(f"- [AWS Documentation]({finding.aws_doc_reference})\n")
                            f.write(f"- [Terraform Documentation]({finding.terraform_doc_reference})\n\n")
                            f.write("---\n\n")
            
            # Quick Wins
            f.write("## Quick Wins\n\n")
            f.write("These findings are low effort but provide significant security value:\n\n")
            
            if quick_wins:
                for i, finding in enumerate(quick_wins, 1):
                    f.write(f"{i}. **{finding.title}** ({finding.module})\n")
                    f.write(f"   - Severity: {finding.severity.value.title()}\n")
                    f.write(f"   - Resource: `{finding.resource}`\n")
                    f.write(f"   - Effort: {finding.effort.title()}\n\n")
            else:
                f.write("No quick wins identified.\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("### Priority 1: Critical and High Severity Findings\n\n")
            
            critical_high = self.get_findings_by_severity(Severity.CRITICAL) + \
                           self.get_findings_by_severity(Severity.HIGH)
            
            if critical_high:
                for finding in critical_high:
                    f.write(f"- **{finding.title}** ({finding.module})\n")
                    f.write(f"  - Effort: {finding.effort.title()}\n")
                    f.write(f"  - Breaking: {'Yes' if finding.breaking_change else 'No'}\n\n")
            else:
                f.write("No critical or high severity findings.\n\n")
            
            f.write("### Priority 2: Medium Severity Findings\n\n")
            medium = self.get_findings_by_severity(Severity.MEDIUM)
            
            if medium:
                for finding in medium:
                    f.write(f"- **{finding.title}** ({finding.module})\n")
                    f.write(f"  - Effort: {finding.effort.title()}\n")
                    f.write(f"  - Breaking: {'Yes' if finding.breaking_change else 'No'}\n\n")
            else:
                f.write("No medium severity findings.\n\n")
            
            f.write("### Priority 3: Low Severity Findings\n\n")
            low = self.get_findings_by_severity(Severity.LOW)
            
            if low:
                for finding in low:
                    f.write(f"- **{finding.title}** ({finding.module})\n")
                    f.write(f"  - Effort: {finding.effort.title()}\n")
                    f.write(f"  - Breaking: {'Yes' if finding.breaking_change else 'No'}\n\n")
            else:
                f.write("No low severity findings.\n\n")
            
            # References
            f.write("## References\n\n")
            f.write("### AWS Documentation\n\n")
            f.write("- [CloudTrail Security Best Practices](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html)\n")
            f.write("- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)\n")
            f.write("- [KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)\n")
            f.write("- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)\n\n")
            
            f.write("### Terraform Documentation\n\n")
            f.write("- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)\n")
            f.write("- [CloudTrail Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail)\n")
            f.write("- [S3 Bucket Resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)\n")
            f.write("- [KMS Key Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key)\n\n")


def audit_cloudtrail_module(module_path: str = "modules/cloudtrail") -> List[Finding]:
    """
    Audit CloudTrail module configuration against AWS best practices
    
    Args:
        module_path: Path to the CloudTrail module directory
        
    Returns:
        List of audit findings
    """
    findings = []
    
    # Finding 1: Missing aws:SourceArn condition in S3 bucket policy
    findings.append(Finding(
        module="cloudtrail",
        resource="aws_s3_bucket_policy.cloudtrail",
        severity=Severity.HIGH,
        category=Category.ACCESS_CONTROL,
        title="S3 bucket policy missing aws:SourceArn condition",
        description="The S3 bucket policy for CloudTrail logs does not include an aws:SourceArn condition key. "
                    "This is a security best practice to prevent unauthorized accounts from writing logs to your bucket. "
                    "AWS recommends adding this condition to ensure only your specific CloudTrail can write to the bucket.",
        current_config="""resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  policy = jsonencode({
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail.arn
      }
    ]
  })
}""",
        recommended_config="""resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  policy = jsonencode({
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail.arn
        Condition = {
          StringEquals = {
            "aws:SourceArn" = "arn:aws:cloudtrail:$${data.aws_region.current.name}:$${data.aws_caller_identity.current.account_id}:trail/$${var.environment}-cloudtrail"
          }
        }
      }
    ]
  })
}""",
        aws_doc_reference="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 2: Missing aws:SourceArn condition in SNS topic policy
    findings.append(Finding(
        module="cloudtrail",
        resource="aws_sns_topic_policy.cloudtrail",
        severity=Severity.HIGH,
        category=Category.ACCESS_CONTROL,
        title="SNS topic policy missing aws:SourceArn condition",
        description="The SNS topic policy does not include an aws:SourceArn condition key. "
                    "This helps prevent unauthorized account access to your SNS topic. "
                    "AWS recommends adding this condition as a security best practice.",
        current_config="""resource "aws_sns_topic_policy" "cloudtrail" {
  arn = aws_sns_topic.cloudtrail.arn
  policy = jsonencode({
    Statement = [{
      Sid    = "AWSCloudTrailSNSPolicy"
      Effect = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
      Action   = "SNS:Publish"
      Resource = aws_sns_topic.cloudtrail.arn
    }]
  })
}""",
        recommended_config="""resource "aws_sns_topic_policy" "cloudtrail" {
  arn = aws_sns_topic.cloudtrail.arn
  policy = jsonencode({
    Statement = [{
      Sid    = "AWSCloudTrailSNSPolicy"
      Effect = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
      Action   = "SNS:Publish"
      Resource = aws_sns_topic.cloudtrail.arn
      Condition = {
        StringEquals = {
          "aws:SourceArn" = "arn:aws:cloudtrail:$${data.aws_region.current.name}:$${data.aws_caller_identity.current.account_id}:trail/$${var.environment}-cloudtrail"
        }
      }
    }]
  })
}""",
        aws_doc_reference="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-permissions-for-sns-notifications.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_policy",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 3: Missing include_global_service_events configuration
    findings.append(Finding(
        module="cloudtrail",
        resource="aws_cloudtrail.main",
        severity=Severity.MEDIUM,
        category=Category.CONFIGURATION,
        title="Missing explicit include_global_service_events configuration",
        description="The CloudTrail trail does not explicitly set include_global_service_events. "
                    "While it defaults to true, AWS best practices recommend explicitly setting this to true "
                    "to ensure events from global services like IAM are captured. This is especially important "
                    "for security monitoring and compliance.",
        current_config="""resource "aws_cloudtrail" "main" {
  name                       = "$${var.environment}-cloudtrail"
  s3_bucket_name             = aws_s3_bucket.cloudtrail.id
  is_multi_region_trail      = true
  enable_log_file_validation = true
  # include_global_service_events not explicitly set
}""",
        recommended_config="""resource "aws_cloudtrail" "main" {
  name                          = "$${var.environment}-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  is_multi_region_trail         = true
  include_global_service_events = true
  enable_log_file_validation    = true
}""",
        aws_doc_reference="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html#cloudtrail-concepts-global-service-events",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail#include_global_service_events",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 4: Consider using advanced event selectors
    findings.append(Finding(
        module="cloudtrail",
        resource="aws_cloudtrail.main",
        severity=Severity.LOW,
        category=Category.CONFIGURATION,
        title="Consider using advanced event selectors for better control",
        description="The module uses basic event selectors. Advanced event selectors provide more granular control "
                    "over which events are logged, can reduce costs by filtering unnecessary events, and support "
                    "additional event types. Consider migrating to advanced event selectors for better flexibility.",
        current_config="""event_selector {
  read_write_type           = "All"
  include_management_events = true
  dynamic "data_resource" {
    for_each = var.enable_s3_data_events ? [1] : []
    content {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3"]
    }
  }
}""",
        recommended_config="""advanced_event_selector {
  name = "Log all management events"
  field_selector {
    field  = "eventCategory"
    equals = ["Management"]
  }
}

dynamic "advanced_event_selector" {
  for_each = var.enable_s3_data_events ? [1] : []
  content {
    name = "Log S3 data events"
    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }
    field_selector {
      field  = "resources.type"
      equals = ["AWS::S3::Object"]
    }
  }
}""",
        aws_doc_reference="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail#advanced_event_selector",
        breaking_change=True,
        effort="medium"
    ))
    
    # Finding 5: Consider enabling CloudTrail Insights
    findings.append(Finding(
        module="cloudtrail",
        resource="aws_cloudtrail.main",
        severity=Severity.LOW,
        category=Category.MONITORING,
        title="CloudTrail Insights not enabled",
        description="CloudTrail Insights helps identify unusual operational activity by analyzing CloudTrail events. "
                    "It can detect anomalies like spikes in resource provisioning, bursts of IAM actions, or gaps in "
                    "periodic maintenance activity. This is valuable for security monitoring and threat detection.",
        current_config="""resource "aws_cloudtrail" "main" {
  name                       = "$${var.environment}-cloudtrail"
  # No insight_selector configured
}""",
        recommended_config="""resource "aws_cloudtrail" "main" {
  name                       = "$${var.environment}-cloudtrail"
  
  insight_selector {
    insight_type = "ApiCallRateInsight"
  }
  
  insight_selector {
    insight_type = "ApiErrorRateInsight"
  }
}""",
        aws_doc_reference="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-insights-events-with-cloudtrail.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail#insight_selector",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 6: S3 bucket lacks MFA delete protection
    findings.append(Finding(
        module="cloudtrail",
        resource="aws_s3_bucket.cloudtrail",
        severity=Severity.MEDIUM,
        category=Category.ACCESS_CONTROL,
        title="S3 bucket does not have MFA delete enabled",
        description="MFA delete adds an extra layer of protection for CloudTrail logs. When enabled, attempts to "
                    "change the versioning state or delete object versions require additional authentication. "
                    "This prevents unauthorized deletion of audit logs even if credentials are compromised. "
                    "Note: MFA delete can only be enabled by the root account user via AWS CLI.",
        current_config="""resource "aws_s3_bucket_versioning" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  versioning_configuration {
    status = "Enabled"
  }
}""",
        recommended_config="""# MFA delete must be enabled via AWS CLI by root account:
# aws s3api put-bucket-versioning \\
#   --bucket <bucket-name> \\
#   --versioning-configuration Status=Enabled,MFADelete=Enabled \\
#   --mfa "arn:aws:iam::ACCOUNT-ID:mfa/root-account-mfa-device XXXXXX"

# Add to bucket policy to require MFA for delete operations:
resource "aws_s3_bucket_policy" "cloudtrail" {
  policy = jsonencode({
    Statement = [{
      Sid    = "RequireMFAForDelete"
      Effect = "Deny"
      Principal = "*"
      Action = ["s3:DeleteObject", "s3:DeleteObjectVersion"]
      Resource = "$${aws_s3_bucket.cloudtrail.arn}/*"
      Condition = {
        BoolIfExists = {
          "aws:MultiFactorAuthPresent" = "false"
        }
      }
    }]
  })
}""",
        aws_doc_reference="https://docs.aws.amazon.com/AmazonS3/latest/userguide/MultiFactorAuthenticationDelete.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning",
        breaking_change=False,
        effort="high"
    ))
    
    # Finding 7: KMS key policy could be more restrictive
    findings.append(Finding(
        module="cloudtrail",
        resource="aws_kms_key.cloudtrail",
        severity=Severity.MEDIUM,
        category=Category.ACCESS_CONTROL,
        title="KMS key policy allows broad service access",
        description="The KMS key policy allows both CloudTrail and SNS services without restricting to specific "
                    "resources. Consider adding condition keys to restrict access to only your specific trail and topic.",
        current_config="""Principal = {
  Service = [
    "cloudtrail.amazonaws.com",
    "sns.amazonaws.com"
  ]
}
Action = ["kms:GenerateDataKey*", "kms:Encrypt*", ...]
Resource = "*"
# No conditions""",
        recommended_config="""Principal = {
  Service = "cloudtrail.amazonaws.com"
}
Action = ["kms:GenerateDataKey*", "kms:Decrypt*"]
Resource = "*"
Condition = {
  StringEquals = {
    "kms:EncryptionContext:aws:cloudtrail:arn" = "arn:aws:cloudtrail:$${data.aws_region.current.name}:$${data.aws_caller_identity.current.account_id}:trail/$${var.environment}-cloudtrail"
  }
}""",
        aws_doc_reference="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-kms-key-policy-for-cloudtrail.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key",
        breaking_change=False,
        effort="medium"
    ))
    
    return findings


def audit_config_module(module_path: str = "modules/config") -> List[Finding]:
    """
    Audit AWS Config module configuration against AWS best practices
    
    Args:
        module_path: Path to the Config module directory
        
    Returns:
        List of audit findings
    """
    findings = []
    
    # Finding 1: IAM role policy uses wildcard s3:* action
    findings.append(Finding(
        module="config",
        resource="aws_iam_role_policy.config_bucket",
        severity=Severity.HIGH,
        category=Category.ACCESS_CONTROL,
        title="IAM role policy uses overly permissive s3:* wildcard action",
        description="The IAM role policy for AWS Config uses 's3:*' which grants all S3 permissions. "
                    "This violates the principle of least privilege. AWS Config only needs specific S3 actions: "
                    "GetBucketAcl, PutObject, and GetBucketLocation. Restricting to these specific actions "
                    "reduces the risk if the role is compromised.",
        current_config="""resource "aws_iam_role_policy" "config_bucket" {
  name = "${var.environment}-${local.service_name}-bucket-policy"
  role = aws_iam_role.config.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          aws_s3_bucket.config.arn,
          "${aws_s3_bucket.config.arn}/*"
        ]
      }
    ]
  })
}""",
        recommended_config="""resource "aws_iam_role_policy" "config_bucket" {
  name = "${var.environment}-${local.service_name}-bucket-policy"
  role = aws_iam_role.config.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSConfigBucketPermissions"
        Effect = "Allow"
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketLocation"
        ]
        Resource = aws_s3_bucket.config.arn
      },
      {
        Sid    = "AWSConfigObjectPermissions"
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.config.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-policy.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 2: Missing AWS Config managed policy attachment
    findings.append(Finding(
        module="config",
        resource="aws_iam_role.config",
        severity=Severity.HIGH,
        category=Category.ACCESS_CONTROL,
        title="IAM role missing AWS managed policy for Config service",
        description="The IAM role for AWS Config does not attach the AWS managed policy "
                    "'AWS_ConfigRole' (arn:aws:iam::aws:policy/service-role/AWS_ConfigRole). "
                    "This managed policy provides the necessary permissions for AWS Config to access "
                    "AWS resources and record their configurations. Without it, Config may not be able "
                    "to properly discover and record all resource types.",
        current_config="""resource "aws_iam_role" "config" {
  name = "${var.environment}-${local.service_name}-role"
  assume_role_policy = jsonencode({...})
  # No managed policy attachment
}

resource "aws_iam_role_policy" "config_bucket" {
  # Only has S3 permissions
}""",
        recommended_config="""resource "aws_iam_role" "config" {
  name = "${var.environment}-${local.service_name}-role"
  assume_role_policy = jsonencode({...})
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "config_policy" {
  role       = aws_iam_role.config.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}

resource "aws_iam_role_policy" "config_bucket" {
  # S3 permissions for delivery channel
}""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/iamrole-permissions.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 3: Missing SNS topic for Config notifications
    findings.append(Finding(
        module="config",
        resource="aws_config_delivery_channel.main",
        severity=Severity.MEDIUM,
        category=Category.MONITORING,
        title="Delivery channel missing SNS topic for notifications",
        description="The AWS Config delivery channel does not have an SNS topic configured. "
                    "SNS notifications allow you to receive real-time alerts when configuration changes occur "
                    "or when compliance status changes. This is important for security monitoring and incident response.",
        current_config="""resource "aws_config_delivery_channel" "main" {
  name           = "${var.environment}-${local.service_name}-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config.id
  # No sns_topic_arn configured
  depends_on = [aws_config_configuration_recorder.main]
}""",
        recommended_config="""resource "aws_sns_topic" "config" {
  name              = "${var.environment}-${local.service_name}-notifications"
  kms_master_key_id = aws_kms_key.config.id
  tags              = local.common_tags
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.environment}-${local.service_name}-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config.id
  sns_topic_arn  = aws_sns_topic.config.arn
  
  snapshot_delivery_properties {
    delivery_frequency = "TwentyFour_Hours"
  }
  
  depends_on = [aws_config_configuration_recorder.main]
}""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/notifications-for-AWS-Config.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/config_delivery_channel#sns_topic_arn",
        breaking_change=False,
        effort="medium"
    ))
    
    # Finding 4: Missing snapshot delivery frequency configuration
    findings.append(Finding(
        module="config",
        resource="aws_config_delivery_channel.main",
        severity=Severity.LOW,
        category=Category.CONFIGURATION,
        title="Delivery channel missing snapshot delivery frequency",
        description="The delivery channel does not explicitly configure snapshot_delivery_properties. "
                    "While AWS Config continuously records changes, periodic snapshots provide a complete "
                    "view of your resource configurations at regular intervals. This is useful for compliance "
                    "reporting and historical analysis. AWS recommends setting an appropriate delivery frequency.",
        current_config="""resource "aws_config_delivery_channel" "main" {
  name           = "${var.environment}-${local.service_name}-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config.id
  # No snapshot_delivery_properties configured
  depends_on = [aws_config_configuration_recorder.main]
}""",
        recommended_config="""resource "aws_config_delivery_channel" "main" {
  name           = "${var.environment}-${local.service_name}-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config.id
  
  snapshot_delivery_properties {
    delivery_frequency = "TwentyFour_Hours"  # or Six_Hours, Twelve_Hours, etc.
  }
  
  depends_on = [aws_config_configuration_recorder.main]
}""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/how-does-config-work.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/config_delivery_channel#snapshot_delivery_properties",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 5: Missing S3 bucket policy for Config service
    findings.append(Finding(
        module="config",
        resource="aws_s3_bucket.config",
        severity=Severity.HIGH,
        category=Category.ACCESS_CONTROL,
        title="S3 bucket missing bucket policy for AWS Config service",
        description="The S3 bucket does not have a bucket policy that explicitly grants AWS Config service "
                    "the necessary permissions. While the IAM role has S3 permissions, a bucket policy provides "
                    "an additional layer of security by restricting access at the bucket level and ensuring "
                    "only the Config service from your account can write to it.",
        current_config="""resource "aws_s3_bucket" "config" {
  bucket        = local.bucket_name
  force_destroy = false
  tags = local.common_tags
}
# No aws_s3_bucket_policy resource""",
        recommended_config="""resource "aws_s3_bucket" "config" {
  bucket        = local.bucket_name
  force_destroy = false
  tags = local.common_tags
}

resource "aws_s3_bucket_policy" "config" {
  bucket = aws_s3_bucket.config.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSConfigBucketPermissionsCheck"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.config.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      },
      {
        Sid    = "AWSConfigBucketExistenceCheck"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:ListBucket"
        Resource = aws_s3_bucket.config.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      },
      {
        Sid    = "AWSConfigBucketDelivery"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.config.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl"      = "bucket-owner-full-control"
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-policy.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 6: KMS key policy allows overly broad principal
    findings.append(Finding(
        module="config",
        resource="aws_kms_key.config",
        severity=Severity.MEDIUM,
        category=Category.ACCESS_CONTROL,
        title="KMS key policy contains overly permissive wildcard principal",
        description="The KMS key policy includes a statement with Principal 'AWS: *' which allows any AWS principal "
                    "to use the key for encryption/decryption operations. While there's a Checkov skip comment, "
                    "this is still a security concern. The policy should be more restrictive and only allow "
                    "specific principals or services that need access to the key.",
        current_config="""resource "aws_kms_key" "config" {
  #checkov:skip=CKV_AWS_33: wildcard principal is allowed for internal config key
  policy = jsonencode({
    Statement = [
      {
        Sid    = "AllowAccountUsage"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}""",
        recommended_config="""resource "aws_kms_key" "config" {
  policy = jsonencode({
    Statement = [
      {
        Sid    = "AllowAccountUsage"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = [
              "s3.${local.region}.amazonaws.com",
              "config.${local.region}.amazonaws.com"
            ]
          }
        }
      }
    ]
  })
}""",
        aws_doc_reference="https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 7: Missing recording mode configuration
    findings.append(Finding(
        module="config",
        resource="aws_config_configuration_recorder.main",
        severity=Severity.LOW,
        category=Category.CONFIGURATION,
        title="Configuration recorder missing recording mode configuration",
        description="The configuration recorder does not specify a recording_mode. AWS Config now supports "
                    "both continuous and periodic recording modes. Continuous recording (default) records changes "
                    "as they happen, while periodic recording can reduce costs by recording daily snapshots. "
                    "Explicitly configuring this helps document your recording strategy and allows for "
                    "resource-specific overrides.",
        current_config="""resource "aws_config_configuration_recorder" "main" {
  name     = "${var.environment}-${local.service_name}-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = var.include_global_resources
  }
  # No recording_mode configured
}""",
        recommended_config="""resource "aws_config_configuration_recorder" "main" {
  name     = "${var.environment}-${local.service_name}-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = var.include_global_resources
  }
  
  recording_mode {
    recording_frequency = "CONTINUOUS"
    
    # Optional: Override for specific resource types
    # recording_mode_override {
    #   description         = "Record EC2 instances daily to reduce costs"
    #   resource_types      = ["AWS::EC2::Instance"]
    #   recording_frequency = "DAILY"
    # }
  }
}""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/stop-start-recorder.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/config_configuration_recorder#recording_mode",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 8: Consider adding Config Rules for compliance
    findings.append(Finding(
        module="config",
        resource="modules/config",
        severity=Severity.MEDIUM,
        category=Category.COMPLIANCE,
        title="No AWS Config Rules defined for compliance monitoring",
        description="The Config module does not include any AWS Config Rules. Config Rules allow you to "
                    "automatically evaluate resource configurations against desired settings and compliance standards. "
                    "Consider adding managed rules for common security checks like encrypted volumes, "
                    "required tags, or CIS benchmark compliance.",
        current_config="""# No aws_config_config_rule resources defined""",
        recommended_config="""# Example: Require encrypted EBS volumes
resource "aws_config_config_rule" "encrypted_volumes" {
  name = "${var.environment}-encrypted-volumes"

  source {
    owner             = "AWS"
    source_identifier = "ENCRYPTED_VOLUMES"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

# Example: Require specific tags
resource "aws_config_config_rule" "required_tags" {
  name = "${var.environment}-required-tags"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "ManagedBy"
  })

  depends_on = [aws_config_configuration_recorder.main]
}""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/config_config_rule",
        breaking_change=False,
        effort="medium"
    ))
    
    # Finding 9: S3 bucket logging logs to same bucket
    findings.append(Finding(
        module="config",
        resource="aws_s3_bucket_logging.config",
        severity=Severity.MEDIUM,
        category=Category.LOGGING,
        title="S3 bucket logging configured to log to itself",
        description="The S3 bucket is configured to store access logs in the same bucket. While this works, "
                    "AWS best practices recommend using a separate dedicated logging bucket. This prevents "
                    "log entries from generating additional log entries (recursive logging) and makes it easier "
                    "to manage retention policies separately for logs vs. data.",
        current_config="""resource "aws_s3_bucket_logging" "config" {
  bucket        = aws_s3_bucket.config.id
  target_bucket = aws_s3_bucket.config.id
  target_prefix = "config-logs/"
}""",
        recommended_config="""# Create separate logging bucket
resource "aws_s3_bucket" "config_logs" {
  bucket = "${local.bucket_name}-logs"
  tags   = local.common_tags
}

resource "aws_s3_bucket_versioning" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.config.arn
    }
  }
}

resource "aws_s3_bucket_logging" "config" {
  bucket        = aws_s3_bucket.config.id
  target_bucket = aws_s3_bucket.config_logs.id
  target_prefix = "config-access-logs/"
}""",
        aws_doc_reference="https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_logging",
        breaking_change=False,
        effort="medium"
    ))
    
    # Finding 10: Missing S3 bucket object lock for compliance
    findings.append(Finding(
        module="config",
        resource="aws_s3_bucket.config",
        severity=Severity.LOW,
        category=Category.COMPLIANCE,
        title="S3 bucket does not have Object Lock enabled",
        description="The S3 bucket does not have Object Lock configured. Object Lock provides WORM "
                    "(Write-Once-Read-Many) protection for objects, preventing them from being deleted or "
                    "overwritten for a fixed amount of time or indefinitely. This is important for compliance "
                    "requirements and audit log retention. Note: Object Lock can only be enabled at bucket creation.",
        current_config="""resource "aws_s3_bucket" "config" {
  bucket        = local.bucket_name
  force_destroy = false
  tags = local.common_tags
}
# No object_lock_enabled or object_lock_configuration""",
        recommended_config="""resource "aws_s3_bucket" "config" {
  bucket              = local.bucket_name
  force_destroy       = false
  object_lock_enabled = true
  tags                = local.common_tags
}

resource "aws_s3_bucket_object_lock_configuration" "config" {
  bucket = aws_s3_bucket.config.id

  rule {
    default_retention {
      mode = "GOVERNANCE"  # or "COMPLIANCE" for stricter requirements
      days = 365
    }
  }
}""",
        aws_doc_reference="https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_object_lock_configuration",
        breaking_change=True,
        effort="high"
    ))
    
    return findings


def audit_guardduty_module(module_path: str = "modules/guardduty") -> List[Finding]:
    """
    Audit GuardDuty module configuration against AWS best practices
    
    Args:
        module_path: Path to the GuardDuty module directory
        
    Returns:
        List of audit findings
    """
    findings = []
    
    # Finding 1: Using deprecated datasources instead of features
    findings.append(Finding(
        module="guardduty",
        resource="aws_guardduty_detector.main",
        severity=Severity.HIGH,
        category=Category.CONFIGURATION,
        title="Using deprecated datasources block instead of detector features",
        description="The GuardDuty detector uses the deprecated 'datasources' block. AWS deprecated this in "
                    "March 2023 in favor of the 'aws_guardduty_detector_feature' resource. The datasources "
                    "approach is less flexible and doesn't support newer protection plans like Runtime Monitoring, "
                    "Lambda Protection, and RDS Protection. Migrating to detector features provides better control "
                    "and access to all GuardDuty protection capabilities.",
        current_config="""resource "aws_guardduty_detector" "main" {
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
}""",
        recommended_config="""resource "aws_guardduty_detector" "main" {
  enable                       = true
  finding_publishing_frequency = var.finding_publishing_frequency
  tags                         = local.common_tags
}

resource "aws_guardduty_detector_feature" "s3_protection" {
  detector_id = aws_guardduty_detector.main.id
  name        = "S3_DATA_EVENTS"
  status      = var.enable_s3_logs ? "ENABLED" : "DISABLED"
}

resource "aws_guardduty_detector_feature" "eks_audit_logs" {
  detector_id = aws_guardduty_detector.main.id
  name        = "EKS_AUDIT_LOGS"
  status      = var.enable_kubernetes_logs ? "ENABLED" : "DISABLED"
}

resource "aws_guardduty_detector_feature" "ebs_malware_protection" {
  detector_id = aws_guardduty_detector.main.id
  name        = "EBS_MALWARE_PROTECTION"
  status      = var.enable_malware_protection ? "ENABLED" : "DISABLED"
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/guardduty-features-activation-model.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_detector_feature",
        breaking_change=True,
        effort="medium"
    ))
    
    # Finding 2: Missing Runtime Monitoring protection
    findings.append(Finding(
        module="guardduty",
        resource="aws_guardduty_detector.main",
        severity=Severity.HIGH,
        category=Category.MONITORING,
        title="Runtime Monitoring protection not enabled",
        description="GuardDuty Runtime Monitoring is not enabled. This feature monitors operating system-level "
                    "events on EC2 instances, EKS clusters, and ECS Fargate tasks to detect runtime threats like "
                    "malware, unauthorized access, and suspicious behavior. Runtime Monitoring provides deeper "
                    "visibility into workload security and can detect threats that foundational data sources miss. "
                    "It includes automated agent management for EC2 and ECS Fargate.",
        current_config="""# Runtime Monitoring not configured
datasources {
  s3_logs { enable = var.enable_s3_logs }
  kubernetes { audit_logs { enable = var.enable_kubernetes_logs } }
  malware_protection { ... }
}""",
        recommended_config="""resource "aws_guardduty_detector_feature" "runtime_monitoring" {
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
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/runtime-monitoring.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_detector_feature",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 3: Missing Lambda Protection
    findings.append(Finding(
        module="guardduty",
        resource="aws_guardduty_detector.main",
        severity=Severity.MEDIUM,
        category=Category.MONITORING,
        title="Lambda Protection not enabled",
        description="GuardDuty Lambda Protection is not enabled. This feature monitors Lambda network activity "
                    "logs to detect threats to Lambda functions, including cryptomining, communication with "
                    "malicious servers, and data exfiltration attempts. As serverless workloads become more common, "
                    "Lambda Protection provides essential visibility into function-level security threats.",
        current_config="""# Lambda Protection not configured""",
        recommended_config="""resource "aws_guardduty_detector_feature" "lambda_protection" {
  detector_id = aws_guardduty_detector.main.id
  name        = "LAMBDA_NETWORK_LOGS"
  status      = "ENABLED"
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/lambda-protection.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_detector_feature",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 4: Missing RDS Protection
    findings.append(Finding(
        module="guardduty",
        resource="aws_guardduty_detector.main",
        severity=Severity.MEDIUM,
        category=Category.MONITORING,
        title="RDS Protection not enabled",
        description="GuardDuty RDS Protection is not enabled. This feature analyzes and profiles RDS login "
                    "activity for potential access threats to Aurora and RDS databases. It can detect anomalous "
                    "login patterns, brute force attacks, and unauthorized access attempts. For environments using "
                    "RDS databases, this provides critical database-level threat detection.",
        current_config="""# RDS Protection not configured""",
        recommended_config="""resource "aws_guardduty_detector_feature" "rds_protection" {
  detector_id = aws_guardduty_detector.main.id
  name        = "RDS_LOGIN_EVENTS"
  status      = "ENABLED"
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/rds-protection.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_detector_feature",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 5: Organization configuration uses deprecated datasources
    findings.append(Finding(
        module="guardduty",
        resource="aws_guardduty_organization_configuration.main",
        severity=Severity.HIGH,
        category=Category.CONFIGURATION,
        title="Organization configuration uses deprecated datasources block",
        description="The GuardDuty organization configuration uses the deprecated 'datasources' block. "
                    "Similar to the detector, this should be migrated to use 'aws_guardduty_organization_configuration_feature' "
                    "resources. This provides better control over which protection plans are auto-enabled for "
                    "member accounts and supports all current GuardDuty features.",
        current_config="""resource "aws_guardduty_organization_configuration" "main" {
  count = var.is_organization_admin_account ? 1 : 0

  detector_id                      = aws_guardduty_detector.main.id
  auto_enable_organization_members = var.auto_enable_organization_members

  datasources {
    s3_logs { auto_enable = var.enable_s3_logs }
    kubernetes { audit_logs { enable = var.enable_kubernetes_logs } }
    malware_protection { ... }
  }
}""",
        recommended_config="""resource "aws_guardduty_organization_configuration" "main" {
  count = var.is_organization_admin_account ? 1 : 0

  detector_id                      = aws_guardduty_detector.main.id
  auto_enable_organization_members = var.auto_enable_organization_members
}

resource "aws_guardduty_organization_configuration_feature" "s3_protection" {
  count = var.is_organization_admin_account ? 1 : 0

  detector_id = aws_guardduty_detector.main.id
  name        = "S3_DATA_EVENTS"
  auto_enable = var.enable_s3_logs ? "ALL" : "NONE"
}

resource "aws_guardduty_organization_configuration_feature" "eks_audit_logs" {
  count = var.is_organization_admin_account ? 1 : 0

  detector_id = aws_guardduty_detector.main.id
  name        = "EKS_AUDIT_LOGS"
  auto_enable = var.enable_kubernetes_logs ? "ALL" : "NONE"
}

resource "aws_guardduty_organization_configuration_feature" "ebs_malware_protection" {
  count = var.is_organization_admin_account ? 1 : 0

  detector_id = aws_guardduty_detector.main.id
  name        = "EBS_MALWARE_PROTECTION"
  auto_enable = var.enable_malware_protection ? "ALL" : "NONE"
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/set-guardduty-auto-enable-preferences.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_organization_configuration_feature",
        breaking_change=True,
        effort="medium"
    ))
    
    # Finding 6: Missing EKS Runtime Monitoring for Extended Threat Detection
    findings.append(Finding(
        module="guardduty",
        resource="aws_guardduty_detector.main",
        severity=Severity.MEDIUM,
        category=Category.MONITORING,
        title="EKS Runtime Monitoring not enabled for Extended Threat Detection",
        description="GuardDuty Extended Threat Detection for EKS requires either EKS Protection (audit logs) "
                    "or Runtime Monitoring to be enabled. While EKS audit logs are enabled, adding EKS Runtime "
                    "Monitoring provides maximum detection coverage by monitoring both control plane (audit logs) "
                    "and data plane (runtime) activities. This enables detection of multi-stage attacks that "
                    "span both layers.",
        current_config="""# Only EKS audit logs enabled
datasources {
  kubernetes {
    audit_logs {
      enable = var.enable_kubernetes_logs
    }
  }
}""",
        recommended_config="""resource "aws_guardduty_detector_feature" "eks_audit_logs" {
  detector_id = aws_guardduty_detector.main.id
  name        = "EKS_AUDIT_LOGS"
  status      = "ENABLED"
}

resource "aws_guardduty_detector_feature" "eks_runtime_monitoring" {
  detector_id = aws_guardduty_detector.main.id
  name        = "EKS_RUNTIME_MONITORING"
  status      = "ENABLED"

  additional_configuration {
    name   = "EKS_ADDON_MANAGEMENT"
    status = "ENABLED"
  }
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/guardduty-extended-threat-detection.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_detector_feature",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 7: Missing SNS topic for GuardDuty findings
    findings.append(Finding(
        module="guardduty",
        resource="modules/guardduty",
        severity=Severity.MEDIUM,
        category=Category.MONITORING,
        title="No SNS topic configured for GuardDuty findings notifications",
        description="The GuardDuty module does not configure an SNS topic for findings notifications. "
                    "While findings are available in the GuardDuty console and can be exported to S3, "
                    "SNS notifications enable real-time alerting for security findings. This is critical "
                    "for incident response and can integrate with other tools like Lambda, email, or "
                    "ticketing systems for automated workflows.",
        current_config="""# No SNS topic or publishing destination configured""",
        recommended_config="""resource "aws_sns_topic" "guardduty_findings" {
  name              = "${var.environment}-guardduty-findings"
  kms_master_key_id = aws_kms_key.guardduty.id
  tags              = local.common_tags
}

resource "aws_sns_topic_policy" "guardduty_findings" {
  arn = aws_sns_topic.guardduty_findings.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowGuardDutyPublish"
        Effect = "Allow"
        Principal = {
          Service = "guardduty.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.guardduty_findings.arn
      }
    ]
  })
}

# Optional: Configure EventBridge rule to send findings to SNS
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "${var.environment}-guardduty-findings"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
  })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.guardduty_findings.arn
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings_cloudwatch.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_publishing_destination",
        breaking_change=False,
        effort="medium"
    ))
    
    # Finding 8: Missing S3 publishing destination for findings
    findings.append(Finding(
        module="guardduty",
        resource="modules/guardduty",
        severity=Severity.LOW,
        category=Category.LOGGING,
        title="No S3 publishing destination configured for findings export",
        description="The GuardDuty module does not configure an S3 publishing destination for exporting findings. "
                    "While findings are stored in GuardDuty for 90 days, exporting to S3 provides long-term "
                    "retention for compliance, historical analysis, and integration with security analytics tools. "
                    "S3 export also enables querying findings with Athena or feeding them into SIEM systems.",
        current_config="""# No aws_guardduty_publishing_destination configured""",
        recommended_config="""resource "aws_s3_bucket" "guardduty_findings" {
  bucket = "${var.environment}-guardduty-findings-${random_id.suffix.dec}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_versioning" "guardduty_findings" {
  bucket = aws_s3_bucket.guardduty_findings.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "guardduty_findings" {
  bucket = aws_s3_bucket.guardduty_findings.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.guardduty.arn
    }
  }
}

resource "aws_guardduty_publishing_destination" "s3" {
  detector_id     = aws_guardduty_detector.main.id
  destination_arn = aws_s3_bucket.guardduty_findings.arn
  kms_key_arn     = aws_kms_key.guardduty.arn

  depends_on = [aws_s3_bucket_policy.guardduty_findings]
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_exportfindings.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_publishing_destination",
        breaking_change=False,
        effort="medium"
    ))
    
    # Finding 9: Consider more frequent finding publishing
    findings.append(Finding(
        module="guardduty",
        resource="aws_guardduty_detector.main",
        severity=Severity.LOW,
        category=Category.MONITORING,
        title="Finding publishing frequency set to default SIX_HOURS",
        description="The GuardDuty detector uses the default finding publishing frequency of SIX_HOURS. "
                    "For production environments with active security monitoring, consider using FIFTEEN_MINUTES "
                    "or ONE_HOUR for faster notification of security findings. This reduces the time between "
                    "threat detection and response, which is critical for limiting the impact of security incidents.",
        current_config="""variable "finding_publishing_frequency" {
  description = "Frequency of notifications about updated findings"
  type        = string
  default     = "SIX_HOURS"
}

resource "aws_guardduty_detector" "main" {
  finding_publishing_frequency = var.finding_publishing_frequency
}""",
        recommended_config="""variable "finding_publishing_frequency" {
  description = "Frequency of notifications about updated findings"
  type        = string
  default     = "FIFTEEN_MINUTES"  # or "ONE_HOUR" for balance

  validation {
    condition     = contains(["FIFTEEN_MINUTES", "ONE_HOUR", "SIX_HOURS"], var.finding_publishing_frequency)
    error_message = "Finding publishing frequency must be FIFTEEN_MINUTES, ONE_HOUR, or SIX_HOURS."
  }
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings_cloudwatch.html#guardduty_findings_cloudwatch_notification_frequency",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_detector#finding_publishing_frequency",
        breaking_change=False,
        effort="low"
    ))
    
    # Finding 10: Missing KMS key for GuardDuty encryption
    findings.append(Finding(
        module="guardduty",
        resource="modules/guardduty",
        severity=Severity.MEDIUM,
        category=Category.ENCRYPTION,
        title="No KMS key defined for GuardDuty findings encryption",
        description="The GuardDuty module does not define a KMS key for encrypting findings. While GuardDuty "
                    "findings are encrypted at rest by default using AWS-managed keys, using a customer-managed "
                    "KMS key provides better control over encryption, enables key rotation, and allows for "
                    "audit trails of key usage. This is especially important for compliance requirements.",
        current_config="""# No KMS key resource defined for GuardDuty""",
        recommended_config="""resource "aws_kms_key" "guardduty" {
  description             = "KMS key for GuardDuty findings encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow GuardDuty to use the key"
        Effect = "Allow"
        Principal = {
          Service = "guardduty.amazonaws.com"
        }
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_kms_alias" "guardduty" {
  name          = "alias/${var.environment}-guardduty"
  target_key_id = aws_kms_key.guardduty.key_id
}""",
        aws_doc_reference="https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_exportfindings.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key",
        breaking_change=False,
        effort="low"
    ))
    
    return findings


def main():
    """Main entry point for audit script"""
    print("AWS Security Baseline Audit")
    print("=" * 50)
    print()
    
    # Initialize audit report
    report = AuditReport()
    
    # Audit CloudTrail module
    print("Auditing CloudTrail module...")
    cloudtrail_findings = audit_cloudtrail_module()
    for finding in cloudtrail_findings:
        report.add_finding(finding)
    print(f"  Found {len(cloudtrail_findings)} findings")
    print()
    
    # Audit Config module
    print("Auditing Config module...")
    config_findings = audit_config_module()
    for finding in config_findings:
        report.add_finding(finding)
    print(f"  Found {len(config_findings)} findings")
    print()
    
    # Audit GuardDuty module
    print("Auditing GuardDuty module...")
    guardduty_findings = audit_guardduty_module()
    for finding in guardduty_findings:
        report.add_finding(finding)
    print(f"  Found {len(guardduty_findings)} findings")
    print()
    
    # Display summary
    summary = report.get_summary()
    print("Audit Summary:")
    print(f"  Total findings: {summary.total_findings}")
    print(f"  Critical: {summary.critical}")
    print(f"  High: {summary.high}")
    print(f"  Medium: {summary.medium}")
    print(f"  Low: {summary.low}")
    print(f"  Modules audited: {', '.join(summary.modules_audited)}")
    print()
    
    # Generate markdown report
    import os
    output_path = os.path.join(os.path.dirname(__file__), "..", ".kiro", "specs", "security-audit-mcp", "config-audit-report.md")
    print(f"Generating audit report: {output_path}")
    report.generate_markdown_report(output_path)
    print("✓ Audit report generated successfully")
    print()
    
    # Display quick wins
    quick_wins = report.get_quick_wins()
    if quick_wins:
        print(f"Quick Wins ({len(quick_wins)} findings):")
        for finding in quick_wins:
            print(f"  - {finding.title} ({finding.severity.value})")
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
