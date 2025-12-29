# AWS Security Baseline Audit

This directory contains the audit infrastructure for analyzing AWS security service modules against best practices.

## Structure

```
audit/
├── audit.py              # Main audit script and orchestration
├── mcp_client.py         # MCP server wrapper functions
├── terraform_parser.py   # Terraform HCL parser utilities
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Components

### audit.py

Main audit script that orchestrates the security audit process. Contains:

- `Finding`: Data structure for audit findings
- `Severity`: Enum for finding severity levels (critical, high, medium, low)
- `Category`: Enum for finding categories (encryption, access_control, logging, monitoring, compliance, configuration)
- `AuditReport`: Manages findings and generates reports
- `AuditSummary`: Summary statistics for audit results

### mcp_client.py

Wrapper functions for querying MCP servers:

- `AWSDocsClient`: Interface for AWS Documentation MCP server
  - `search_documentation()`: Search AWS docs
  - `read_documentation()`: Read specific doc pages
  - `get_recommendations()`: Get related documentation

- `TerraformClient`: Interface for Terraform MCP server
  - `search_providers()`: Search for provider resources
  - `get_provider_details()`: Get resource schemas
  - `get_latest_provider_version()`: Get latest provider version
  - `get_provider_capabilities()`: Get provider capabilities

- `MCPQueryHelper`: High-level helper for common query patterns
  - `get_service_best_practices()`: Query service best practices
  - `get_terraform_resource_schema()`: Get resource schema
  - `validate_resource_arguments()`: Validate resource configuration

### terraform_parser.py

Utilities for parsing Terraform HCL files:

- `TerraformResource`: Represents a parsed Terraform resource
- `TerraformModule`: Represents a parsed Terraform module
- `TerraformParser`: Parser for extracting resources, variables, outputs, and locals
- `parse_terraform_module()`: Convenience function for parsing modules

## Usage

### Parsing a Terraform Module

```python
from terraform_parser import parse_terraform_module

# Parse a module
module = parse_terraform_module("modules/cloudtrail")

# Get all resources of a specific type
s3_buckets = module.get_resources_by_type("aws_s3_bucket")

# Check if resource exists
has_kms = module.has_resource_type("aws_kms_key")

# Get specific resource
trail = module.get_resource("aws_cloudtrail", "main")
if trail:
    print(f"CloudTrail resource found at line {trail.line_number}")
```

### Creating Audit Findings

```python
from audit import Finding, Severity, Category

finding = Finding(
    module="cloudtrail",
    resource="aws_s3_bucket.cloudtrail_logs",
    severity=Severity.HIGH,
    category=Category.ENCRYPTION,
    title="S3 bucket missing KMS encryption",
    description="CloudTrail S3 bucket should use KMS encryption for enhanced security",
    current_config="# No encryption configured",
    recommended_config="server_side_encryption_configuration { ... }",
    aws_doc_reference="https://docs.aws.amazon.com/...",
    terraform_doc_reference="https://registry.terraform.io/...",
    breaking_change=False,
    effort="low"
)
```

### Using MCP Clients

```python
from mcp_client import MCPQueryHelper

helper = MCPQueryHelper()

# Get best practices for a service
practices = helper.get_service_best_practices("CloudTrail")

# Get Terraform resource schema
schema = helper.get_terraform_resource_schema("aws_cloudtrail")

# Validate resource arguments
validation = helper.validate_resource_arguments(
    "aws_cloudtrail",
    ["name", "s3_bucket_name", "enable_logging"]
)
```

## Data Structures

### Finding

```python
{
    "module": "cloudtrail",
    "resource": "aws_s3_bucket.cloudtrail_logs",
    "severity": "high",
    "category": "encryption",
    "title": "Brief description",
    "description": "Detailed explanation",
    "current_config": "Current Terraform code",
    "recommended_config": "Recommended Terraform code",
    "aws_doc_reference": "AWS doc URL",
    "terraform_doc_reference": "Terraform doc URL",
    "breaking_change": false,
    "effort": "low"
}
```

### AuditSummary

```python
{
    "total_findings": 25,
    "critical": 2,
    "high": 8,
    "medium": 10,
    "low": 5,
    "modules_audited": ["cloudtrail", "config", "guardduty", "detective", "securityhub"]
}
```

## Notes

- The MCP client functions are placeholders that will be called through Kiro's MCP integration
- The Terraform parser is simplified and extracts basic resource information
- For production use with complex HCL, consider using `python-hcl2` library
- All findings should include both AWS and Terraform documentation references
- Severity levels should be assigned based on security impact
- Breaking changes should be clearly marked to help with implementation planning

## Requirements

See `requirements.txt` for Python dependencies.
