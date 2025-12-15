#!/usr/bin/env python3
"""
Test script to validate audit infrastructure setup
"""

import sys
from pathlib import Path

# Add audit directory to path
sys.path.insert(0, str(Path(__file__).parent))

from audit import Finding, Severity, Category, AuditReport, AuditSummary
from terraform_parser import TerraformParser, parse_terraform_module
from mcp_client import MCPQueryHelper


def test_finding_creation():
    """Test creating a finding"""
    print("Testing Finding creation...")
    
    finding = Finding(
        module="cloudtrail",
        resource="aws_s3_bucket.test",
        severity=Severity.HIGH,
        category=Category.ENCRYPTION,
        title="Test finding",
        description="Test description",
        current_config="# current",
        recommended_config="# recommended",
        aws_doc_reference="https://docs.aws.amazon.com/test",
        terraform_doc_reference="https://registry.terraform.io/test",
        breaking_change=False,
        effort="low"
    )
    
    assert finding.module == "cloudtrail"
    assert finding.severity == Severity.HIGH
    assert finding.category == Category.ENCRYPTION
    
    # Test to_dict conversion
    finding_dict = finding.to_dict()
    assert finding_dict["severity"] == "high"
    assert finding_dict["category"] == "encryption"
    
    print("✓ Finding creation works")


def test_audit_report():
    """Test audit report functionality"""
    print("Testing AuditReport...")
    
    report = AuditReport()
    
    # Add some test findings
    for i in range(5):
        severity = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.LOW][i]
        finding = Finding(
            module="test_module",
            resource=f"aws_test.resource_{i}",
            severity=severity,
            category=Category.ENCRYPTION,
            title=f"Test finding {i}",
            description="Test",
            current_config="",
            recommended_config="",
            aws_doc_reference="",
            terraform_doc_reference="",
            breaking_change=False,
            effort="low" if i < 2 else "medium"
        )
        report.add_finding(finding)
    
    # Test summary
    summary = report.get_summary()
    assert summary.total_findings == 5
    assert summary.critical == 1
    assert summary.high == 1
    assert summary.medium == 1
    assert summary.low == 2
    
    # Test filtering
    critical_findings = report.get_findings_by_severity(Severity.CRITICAL)
    assert len(critical_findings) == 1
    
    # Test quick wins
    quick_wins = report.get_quick_wins()
    assert len(quick_wins) == 1  # Only the high severity with low effort
    
    print("✓ AuditReport works")


def test_terraform_parser():
    """Test Terraform parser"""
    print("Testing TerraformParser...")
    
    parser = TerraformParser()
    
    # Test block content extraction
    content = "resource \"aws_s3_bucket\" \"test\" { bucket = \"test\" }"
    block = parser._extract_block_content(content, content.index('{') + 1)
    assert "bucket" in block
    
    # Test attribute parsing
    attrs = parser._parse_attributes("bucket = \"test\"\nversioning = true")
    assert "bucket" in attrs
    
    print("✓ TerraformParser basic functions work")


def test_mcp_helper():
    """Test MCP helper initialization"""
    print("Testing MCPQueryHelper...")
    
    helper = MCPQueryHelper()
    assert helper.aws_docs is not None
    assert helper.terraform is not None
    
    print("✓ MCPQueryHelper initializes")


def test_severity_enum():
    """Test Severity enum"""
    print("Testing Severity enum...")
    
    assert Severity.CRITICAL.value == "critical"
    assert Severity.HIGH.value == "high"
    assert Severity.MEDIUM.value == "medium"
    assert Severity.LOW.value == "low"
    
    print("✓ Severity enum works")


def test_category_enum():
    """Test Category enum"""
    print("Testing Category enum...")
    
    assert Category.ENCRYPTION.value == "encryption"
    assert Category.ACCESS_CONTROL.value == "access_control"
    assert Category.LOGGING.value == "logging"
    assert Category.MONITORING.value == "monitoring"
    assert Category.COMPLIANCE.value == "compliance"
    assert Category.CONFIGURATION.value == "configuration"
    
    print("✓ Category enum works")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Audit Infrastructure")
    print("=" * 60)
    print()
    
    try:
        test_severity_enum()
        test_category_enum()
        test_finding_creation()
        test_audit_report()
        test_terraform_parser()
        test_mcp_helper()
        
        print()
        print("=" * 60)
        print("✓ All infrastructure tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
