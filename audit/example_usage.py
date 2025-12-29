#!/usr/bin/env python3
"""
Example usage of the audit infrastructure

This demonstrates how to use the audit utilities to analyze Terraform modules.
"""

import sys
from pathlib import Path

# Add audit directory to path
sys.path.insert(0, str(Path(__file__).parent))

from audit import Finding, Severity, Category, AuditReport
from terraform_parser import parse_terraform_module
from mcp_client import MCPQueryHelper


def example_parse_module():
    """Example: Parse a Terraform module"""
    print("Example 1: Parsing a Terraform module")
    print("-" * 60)
    
    # Parse the CloudTrail module
    module = parse_terraform_module("modules/cloudtrail")
    
    print(f"Module: {module.module_path}")
    print(f"Total resources: {len(module.resources)}")
    print(f"Total variables: {len(module.variables)}")
    print(f"Total outputs: {len(module.outputs)}")
    print()
    
    # Get S3 buckets
    s3_buckets = module.get_resources_by_type("aws_s3_bucket")
    print(f"S3 buckets found: {len(s3_buckets)}")
    for bucket in s3_buckets:
        print(f"  - {bucket.full_name} (line {bucket.line_number})")
    print()
    
    # Check for KMS keys
    kms_keys = module.get_resources_by_type("aws_kms_key")
    print(f"KMS keys found: {len(kms_keys)}")
    for key in kms_keys:
        print(f"  - {key.full_name}")
        # Check for key rotation
        if key.has_attribute("enable_key_rotation"):
            print(f"    Key rotation: {key.get_attribute('enable_key_rotation')}")
    print()


def example_create_findings():
    """Example: Create audit findings"""
    print("Example 2: Creating audit findings")
    print("-" * 60)
    
    report = AuditReport()
    
    # Create a critical finding
    finding1 = Finding(
        module="cloudtrail",
        resource="aws_s3_bucket.cloudtrail_logs",
        severity=Severity.CRITICAL,
        category=Category.ENCRYPTION,
        title="S3 bucket missing encryption",
        description="CloudTrail S3 bucket must use KMS encryption for compliance",
        current_config="# No encryption configured",
        recommended_config="""
resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.cloudtrail.arn
    }
  }
}
""",
        aws_doc_reference="https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration",
        breaking_change=False,
        effort="low"
    )
    report.add_finding(finding1)
    
    # Create a high severity finding
    finding2 = Finding(
        module="cloudtrail",
        resource="aws_cloudtrail.main",
        severity=Severity.HIGH,
        category=Category.LOGGING,
        title="CloudTrail missing CloudWatch Logs integration",
        description="CloudTrail should send logs to CloudWatch for real-time monitoring",
        current_config="# No CloudWatch Logs configured",
        recommended_config="""
resource "aws_cloudtrail" "main" {
  # ... other config ...
  cloud_watch_logs_group_arn = aws_cloudwatch_log_group.cloudtrail.arn
  cloud_watch_logs_role_arn  = aws_iam_role.cloudtrail_cloudwatch.arn
}
""",
        aws_doc_reference="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/send-cloudtrail-events-to-cloudwatch-logs.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail",
        breaking_change=False,
        effort="medium"
    )
    report.add_finding(finding2)
    
    # Create a medium severity finding
    finding3 = Finding(
        module="config",
        resource="aws_config_configuration_recorder.main",
        severity=Severity.MEDIUM,
        category=Category.MONITORING,
        title="Config recorder missing global resource recording",
        description="Config should record global resources like IAM for complete visibility",
        current_config="# Global resources not explicitly enabled",
        recommended_config="""
resource "aws_config_configuration_recorder" "main" {
  # ... other config ...
  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}
""",
        aws_doc_reference="https://docs.aws.amazon.com/config/latest/developerguide/select-resources.html",
        terraform_doc_reference="https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/config_configuration_recorder",
        breaking_change=False,
        effort="low"
    )
    report.add_finding(finding3)
    
    # Display summary
    summary = report.get_summary()
    print(f"Total findings: {summary.total_findings}")
    print(f"  Critical: {summary.critical}")
    print(f"  High: {summary.high}")
    print(f"  Medium: {summary.medium}")
    print(f"  Low: {summary.low}")
    print(f"Modules audited: {', '.join(summary.modules_audited)}")
    print()
    
    # Show quick wins
    quick_wins = report.get_quick_wins()
    print(f"Quick wins (low effort, high/medium severity): {len(quick_wins)}")
    for qw in quick_wins:
        print(f"  - {qw.title} ({qw.severity.value})")
    print()


def example_mcp_helper():
    """Example: Using MCP helper"""
    print("Example 3: Using MCP Query Helper")
    print("-" * 60)
    
    helper = MCPQueryHelper()
    
    print("MCP Query Helper initialized")
    print("  - AWS Docs client: Ready")
    print("  - Terraform client: Ready")
    print()
    
    print("Note: Actual MCP queries will be made through Kiro's MCP integration")
    print("      during the audit execution.")
    print()


def main():
    """Run all examples"""
    print("=" * 60)
    print("Audit Infrastructure Usage Examples")
    print("=" * 60)
    print()
    
    try:
        example_parse_module()
        print()
        example_create_findings()
        print()
        example_mcp_helper()
        
        print("=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
