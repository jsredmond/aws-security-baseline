#!/bin/bash
# Run all property-based tests for CloudTrail module

set -e

echo "=========================================="
echo "Running All CloudTrail Module Tests"
echo "=========================================="
echo ""

TOTAL_PASS=0
TOTAL_FAIL=0

# Test 1: Module Structure
echo "Test 1: Module Structure Completeness"
echo "--------------------------------------"
if ./test_module_structure.sh; then
    ((TOTAL_PASS++))
else
    ((TOTAL_FAIL++))
fi
echo ""

# Test 2: Resource Encapsulation
echo "Test 2: Resource Encapsulation"
echo "-------------------------------"
if ./test_resource_encapsulation.sh; then
    ((TOTAL_PASS++))
else
    ((TOTAL_FAIL++))
fi
echo ""

# Test 3: S3 Security Configurations
echo "Test 3: S3 Security Configurations"
echo "-----------------------------------"
if ./test_s3_security.sh; then
    ((TOTAL_PASS++))
else
    ((TOTAL_FAIL++))
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total Tests: $((TOTAL_PASS + TOTAL_FAIL))"
echo "Passed: $TOTAL_PASS"
echo "Failed: $TOTAL_FAIL"
echo ""

if [ $TOTAL_FAIL -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    exit 1
fi
