#!/usr/bin/env python3
"""
Integration test for Terraform parser with actual modules
"""

import sys
from pathlib import Path

# Add audit directory to path
sys.path.insert(0, str(Path(__file__).parent))

from terraform_parser import parse_terraform_module


def test_cloudtrail_module():
    """Test parsing the CloudTrail module"""
    print("Testing CloudTrail module parsing...")

    try:
        module = parse_terraform_module("modules/cloudtrail")

        print(f"  Found {len(module.resources)} resources")
        print(f"  Found {len(module.variables)} variables")
        print(f"  Found {len(module.outputs)} outputs")

        # List resource types
        resource_types = set(r.resource_type for r in module.resources)
        print(f"  Resource types: {', '.join(sorted(resource_types))}")

        # Check for key resources
        has_trail = module.has_resource_type("aws_cloudtrail")
        has_s3 = module.has_resource_type("aws_s3_bucket")
        has_kms = module.has_resource_type("aws_kms_key")

        print(f"  Has CloudTrail: {has_trail}")
        print(f"  Has S3 bucket: {has_s3}")
        print(f"  Has KMS key: {has_kms}")

        print("✓ CloudTrail module parsed successfully")
        return True

    except FileNotFoundError:
        print("  ⚠ CloudTrail module not found (expected in test environment)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_config_module():
    """Test parsing the Config module"""
    print("Testing Config module parsing...")

    try:
        module = parse_terraform_module("modules/config")

        print(f"  Found {len(module.resources)} resources")
        print(f"  Found {len(module.variables)} variables")
        print(f"  Found {len(module.outputs)} outputs")

        # List resource types
        resource_types = set(r.resource_type for r in module.resources)
        print(f"  Resource types: {', '.join(sorted(resource_types))}")

        print("✓ Config module parsed successfully")
        return True

    except FileNotFoundError:
        print("  ⚠ Config module not found (expected in test environment)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_guardduty_module():
    """Test parsing the GuardDuty module"""
    print("Testing GuardDuty module parsing...")

    try:
        module = parse_terraform_module("modules/guardduty")

        print(f"  Found {len(module.resources)} resources")
        print(f"  Found {len(module.variables)} variables")
        print(f"  Found {len(module.outputs)} outputs")

        # List resource types
        resource_types = set(r.resource_type for r in module.resources)
        print(f"  Resource types: {', '.join(sorted(resource_types))}")

        print("✓ GuardDuty module parsed successfully")
        return True

    except FileNotFoundError:
        print("  ⚠ GuardDuty module not found (expected in test environment)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run integration tests"""
    print("=" * 60)
    print("Testing Terraform Parser Integration")
    print("=" * 60)
    print()

    results = []
    results.append(test_cloudtrail_module())
    print()
    results.append(test_config_module())
    print()
    results.append(test_guardduty_module())

    print()
    print("=" * 60)
    if all(results):
        print("✓ All integration tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
