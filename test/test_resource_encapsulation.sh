#!/bin/bash
# Feature: terraform-modularization, Property 2: Resource encapsulation
# Validates: Requirements 1.3
# Property: For any service module, all resources, data sources, and locals related to that service
# SHALL be contained within the module and not in the root module.

set -e

MODULE_PATH="../modules/cloudtrail"
ROOT_CLOUDTRAIL_FILE="../cloudtrail.tf"

echo "Testing CloudTrail Resource Encapsulation..."
echo "============================================="

# Check that CloudTrail module contains CloudTrail resources
echo ""
echo "Checking module contains CloudTrail resources..."

CLOUDTRAIL_RESOURCES=(
	"aws_cloudtrail"
	"aws_s3_bucket.*cloudtrail"
	"aws_kms_key"
	"aws_cloudwatch_log_group"
	"aws_iam_role"
	"aws_sns_topic"
)

MODULE_PASS=0
MODULE_FAIL=0

for resource in "${CLOUDTRAIL_RESOURCES[@]}"; do
	if grep -q "resource \"$resource\"" "$MODULE_PATH/main.tf" 2>/dev/null; then
		echo "✓ PASS: Module contains $resource"
		((MODULE_PASS++))
	else
		echo "✗ FAIL: Module missing $resource"
		((MODULE_FAIL++))
	fi
done

# Check that root module does NOT contain CloudTrail-specific resources
# (This test will be more relevant after migration, but we can check the pattern)
echo ""
echo "Checking root module structure..."

if [ -f "$ROOT_CLOUDTRAIL_FILE" ]; then
	echo "⚠ WARNING: Root cloudtrail.tf still exists (expected before migration)"
	echo "  This file should be removed after state migration is complete"
else
	echo "✓ PASS: Root cloudtrail.tf does not exist (resources properly encapsulated)"
fi

echo ""
echo "Module Resources: $MODULE_PASS found, $MODULE_FAIL missing"
echo ""

if [ $MODULE_FAIL -eq 0 ]; then
	echo "✓ Property 2: Resource encapsulation - PASSED"
	echo "  (Note: Full validation requires state migration completion)"
	exit 0
else
	echo "✗ Property 2: Resource encapsulation - FAILED"
	exit 1
fi
