# Amazon Inspector Terraform Module

This module enables Amazon Inspector for continuous vulnerability scanning of AWS workloads.

## Purpose

Amazon Inspector automatically discovers and scans workloads for:

- Software vulnerabilities (CVEs)
- Network exposure issues
- Unintended network reachability
- Security best practice deviations

## Features

- **Continuous Scanning**: Automatically scans resources as they're deployed
- **Multi-Resource Support**: EC2, ECR, Lambda functions, and Lambda code
- **Risk Scoring**: Prioritizes findings based on CVSS scores and exploitability
- **Security Hub Integration**: Sends findings to Security Hub
- **Automated Discovery**: No agents required for ECR and Lambda

## Usage

### Basic Configuration

```hcl
module "inspector" {
  source = "./modules/inspector"

  environment    = "prod"
  resource_types = ["EC2", "ECR", "LAMBDA"]

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### All Resource Types

```hcl
module "inspector" {
  source = "./modules/inspector"

  environment    = "prod"
  resource_types = ["EC2", "ECR", "LAMBDA", "LAMBDA_CODE"]

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

## Requirements

| Name      | Version   |
| --------- | --------- |
| terraform | >= 1.14.1 |
| aws       | >= 6.25.0 |
| random    | >= 3.7.2  |

## Providers

| Name   | Version   |
| ------ | --------- |
| aws    | >= 6.25.0 |
| random | >= 3.7.2  |

## Inputs

| Name           | Description                           | Type           | Default                    | Required |
| -------------- | ------------------------------------- | -------------- | -------------------------- | :------: |
| environment    | Environment name (dev, staging, prod) | `string`       | n/a                        |   yes    |
| resource_types | Types of resources to scan            | `list(string)` | `["EC2", "ECR", "LAMBDA"]` |    no    |
| common_tags    | Common tags to apply to all resources | `map(string)`  | `{}`                       |    no    |

## Outputs

| Name                   | Description                                 |
| ---------------------- | ------------------------------------------- |
| account_id             | AWS account ID where Inspector is enabled   |
| enabled_resource_types | List of resource types enabled for scanning |
| region                 | AWS region where Inspector is enabled       |

## Resource Types

### EC2

- Scans EC2 instances for software vulnerabilities
- Checks network reachability
- Requires SSM Agent (automatically installed on Amazon Linux 2/2023)

### ECR

- Scans container images for OS and programming language vulnerabilities
- Scans on push and continuously for new CVEs
- No additional configuration required

### LAMBDA

- Scans Lambda function code packages and layers
- Identifies vulnerabilities in application dependencies
- Automatic scanning on deployment

### LAMBDA_CODE

- Deep code scanning for Lambda functions
- Identifies code-level vulnerabilities
- Provides code snippets showing vulnerable code

## Findings

Inspector generates findings for:

- Software vulnerabilities (CVEs) with CVSS scores
- Network paths that allow unintended access
- Missing security patches
- Outdated runtime versions

## Integration

- **Security Hub**: Findings automatically sent for centralized view
- **EventBridge**: Trigger automated remediation workflows
- **Systems Manager**: Patch Manager integration for remediation

## Cost Considerations

Inspector pricing is based on:

- **EC2**: Per instance per month
- **ECR**: Per image scan
- **Lambda**: Per function per month
- **Lambda Code**: Per function scanned

Refer to [Amazon Inspector Pricing](https://aws.amazon.com/inspector/pricing/)

## Notes

- EC2 scanning requires Systems Manager Agent (SSM Agent)
- First 15 days are free for EC2 and Lambda scanning
- Findings are risk-scored to help prioritize remediation
- Supports suppression rules for accepted risks
