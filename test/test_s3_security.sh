#!/bin/bash
# Feature: terraform-modularization, Property 26, 27, 28, 29: S3 security configurations
# Validates: Requirements 7.1, 7.2, 7.3, 7.4
# Property 26: For any S3 bucket resource, there SHALL be a corresponding
#              aws_s3_bucket_versioning resource with status = "Enabled"
# Property 27: For any S3 bucket resource, there SHALL be a corresponding
#              aws_s3_bucket_server_side_encryption_configuration resource with sse_algorithm = "aws:kms"
# Property 28: For any S3 bucket resource, there SHALL be a corresponding
#              aws_s3_bucket_public_access_block resource with all four settings set to true
# Property 29: For any S3 bucket resource, there SHALL be a corresponding
#              aws_s3_bucket_lifecycle_configuration resource

set -e

MODULE_PATH="../modules/cloudtrail/main.tf"

echo "Testing CloudTrail S3 Security Configurations..."
echo "================================================="

PASS_COUNT=0
FAIL_COUNT=0

# Property 26: Check for S3 bucket versioning
echo ""
echo "Property 26: S3 Versioning Configuration"
if grep -q 'resource "aws_s3_bucket_versioning"' "$MODULE_PATH" &&
	grep -A 5 'resource "aws_s3_bucket_versioning"' "$MODULE_PATH" | grep -q 'status.*=.*"Enabled"'; then
	echo "✓ PASS: S3 bucket versioning is configured with status = Enabled"
	((PASS_COUNT++))
else
	echo "✗ FAIL: S3 bucket versioning is not properly configured"
	((FAIL_COUNT++))
fi

# Property 27: Check for S3 encryption configuration
echo ""
echo "Property 27: S3 Encryption Configuration"
if grep -q 'resource "aws_s3_bucket_server_side_encryption_configuration"' "$MODULE_PATH" &&
	grep -A 10 'resource "aws_s3_bucket_server_side_encryption_configuration"' "$MODULE_PATH" | grep -q 'sse_algorithm.*=.*"aws:kms"'; then
	echo "✓ PASS: S3 bucket encryption is configured with sse_algorithm = aws:kms"
	((PASS_COUNT++))
else
	echo "✗ FAIL: S3 bucket encryption is not properly configured"
	((FAIL_COUNT++))
fi

# Property 28: Check for S3 public access block
echo ""
echo "Property 28: S3 Public Access Block"
PUBLIC_ACCESS_CHECKS=0
if grep -q 'resource "aws_s3_bucket_public_access_block"' "$MODULE_PATH"; then
	BLOCK_SECTION=$(grep -A 10 'resource "aws_s3_bucket_public_access_block"' "$MODULE_PATH")

	if echo "$BLOCK_SECTION" | grep -q 'block_public_acls.*=.*true'; then
		((PUBLIC_ACCESS_CHECKS++))
	fi
	if echo "$BLOCK_SECTION" | grep -q 'block_public_policy.*=.*true'; then
		((PUBLIC_ACCESS_CHECKS++))
	fi
	if echo "$BLOCK_SECTION" | grep -q 'ignore_public_acls.*=.*true'; then
		((PUBLIC_ACCESS_CHECKS++))
	fi
	if echo "$BLOCK_SECTION" | grep -q 'restrict_public_buckets.*=.*true'; then
		((PUBLIC_ACCESS_CHECKS++))
	fi

	if [ $PUBLIC_ACCESS_CHECKS -eq 4 ]; then
		echo "✓ PASS: S3 public access block has all four settings set to true"
		((PASS_COUNT++))
	else
		echo "✗ FAIL: S3 public access block is missing some settings ($PUBLIC_ACCESS_CHECKS/4 found)"
		((FAIL_COUNT++))
	fi
else
	echo "✗ FAIL: S3 public access block resource not found"
	((FAIL_COUNT++))
fi

# Property 29: Check for S3 lifecycle configuration
echo ""
echo "Property 29: S3 Lifecycle Configuration"
if grep -q 'resource "aws_s3_bucket_lifecycle_configuration"' "$MODULE_PATH"; then
	echo "✓ PASS: S3 bucket lifecycle configuration is present"
	((PASS_COUNT++))
else
	echo "✗ FAIL: S3 bucket lifecycle configuration is not configured"
	((FAIL_COUNT++))
fi

echo ""
echo "================================================="
echo "Results: $PASS_COUNT passed, $FAIL_COUNT failed"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
	echo "✓ Properties 26-29: S3 security configurations - ALL PASSED"
	exit 0
else
	echo "✗ Properties 26-29: S3 security configurations - SOME FAILED"
	exit 1
fi
