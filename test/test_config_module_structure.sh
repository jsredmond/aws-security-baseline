#!/bin/bash
# Feature: terraform-modularization, Property 1: Module structure completeness
# Validates: Requirements 1.2
# Property: For any service module (cloudtrail, config, detective, guardduty, securityhub),
# the module directory SHALL contain main.tf, variables.tf, outputs.tf, and README.md files.

set -e

MODULE_PATH="../modules/config"
REQUIRED_FILES=("main.tf" "variables.tf" "outputs.tf" "README.md")

echo "Testing Config Module Structure Completeness..."
echo "=================================================="

PASS_COUNT=0
FAIL_COUNT=0

for file in "${REQUIRED_FILES[@]}"; do
	if [ -f "$MODULE_PATH/$file" ]; then
		echo "✓ PASS: $file exists"
		((PASS_COUNT++))
	else
		echo "✗ FAIL: $file is missing"
		((FAIL_COUNT++))
	fi
done

echo ""
echo "Results: $PASS_COUNT passed, $FAIL_COUNT failed"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
	echo "✓ Property 1: Module structure completeness - PASSED"
	exit 0
else
	echo "✗ Property 1: Module structure completeness - FAILED"
	exit 1
fi
