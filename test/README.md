# Terraform Modularization Tests

This directory contains property-based tests for the Terraform modularization project. The tests validate that the modular structure adheres to the requirements and design specifications.

## Test Framework

The tests are implemented as shell scripts that validate Terraform configuration files against the correctness properties defined in the design document.

## Running Tests

### Run All Tests

```bash
cd test
./run_all_tests.sh
```

### Run Individual Tests

```bash
# Test 1: Module Structure Completeness (Property 1)
./test_module_structure.sh

# Test 2: Resource Encapsulation (Property 2)
./test_resource_encapsulation.sh

# Test 3: S3 Security Configurations (Properties 26-29)
./test_s3_security.sh
```

## Test Coverage

### CloudTrail Module Tests

1. **Module Structure Completeness (Property 1)**
   - Validates: Requirements 1.2
   - Verifies that the CloudTrail module contains all required files:
     - main.tf
     - variables.tf
     - outputs.tf
     - README.md

2. **Resource Encapsulation (Property 2)**
   - Validates: Requirements 1.3
   - Verifies that all CloudTrail-related resources are contained within the module:
     - aws_cloudtrail
     - aws_s3_bucket
     - aws_kms_key
     - aws_cloudwatch_log_group
     - aws_iam_role
     - aws_sns_topic

3. **S3 Security Configurations (Properties 26-29)**
   - Validates: Requirements 7.1, 7.2, 7.3, 7.4
   - Property 26: S3 bucket versioning is enabled
   - Property 27: S3 bucket encryption uses aws:kms
   - Property 28: S3 public access block has all four settings enabled
   - Property 29: S3 bucket lifecycle configuration is present

## Test Output

Each test provides detailed output showing:
- Individual check results (PASS/FAIL)
- Summary of passed and failed checks
- Overall test status

Example output:
```bash
✓ PASS: main.tf exists
✓ PASS: variables.tf exists
✓ PASS: outputs.tf exists
✓ PASS: README.md exists

Results: 4 passed, 0 failed

✓ Property 1: Module structure completeness - PASSED
```

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed

## Future Tests

As additional modules are created (Config, GuardDuty, Detective, Security Hub), similar tests should be added to validate:
- Module structure completeness
- Resource encapsulation
- Service-specific security configurations
- Module interface completeness
- Variable and output documentation

## Notes

- Tests are designed to be run during development and in CI/CD pipelines
- Some tests include warnings for expected conditions during migration (e.g., root cloudtrail.tf exists before state migration)
- Tests validate configuration structure, not runtime behavior
- For runtime validation, use `terraform plan` and `terraform apply` in a test environment
