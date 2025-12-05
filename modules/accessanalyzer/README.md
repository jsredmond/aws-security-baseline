# IAM Access Analyzer Terraform Module

This module deploys AWS IAM Access Analyzer to identify resources shared with external entities and detect unused access.

## Purpose

IAM Access Analyzer helps identify unintended access to your resources by:

- Analyzing resource-based policies to find external access
- Identifying unused IAM permissions
- Validating policies against AWS best practices
- Generating least-privilege policies from CloudTrail logs

## Features

- **External Access Detection**: Identifies resources shared outside your account/organization
- **Unused Access Analysis**: Detects IAM permissions that haven't been used
- **Organization Support**: Can analyze entire AWS Organizations
- **Security Hub Integration**: Sends findings to Security Hub for centralized visibility

## Usage

### Account-Level Analyzer

```hcl
module "accessanalyzer" {
  source = "./modules/accessanalyzer"

  environment = "prod"

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### Organization-Level Analyzer

```hcl
module "accessanalyzer" {
  source = "./modules/accessanalyzer"

  environment                = "prod"
  is_organization_analyzer   = true
  enable_unused_access_analyzer = true
  unused_access_age_days     = 90

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

| Name                          | Description                                      | Type          | Default | Required |
| ----------------------------- | ------------------------------------------------ | ------------- | ------- | :------: |
| environment                   | Environment name (dev, staging, prod)            | `string`      | n/a     |   yes    |
| is_organization_analyzer      | Whether to create an organization-level analyzer | `bool`        | `false` |    no    |
| enable_unused_access_analyzer | Enable unused access analyzer                    | `bool`        | `true`  |    no    |
| unused_access_age_days        | Number of days to consider access as unused      | `number`      | `90`    |    no    |
| common_tags                   | Common tags to apply to all resources            | `map(string)` | `{}`    |    no    |

## Outputs

| Name                  | Description                                     |
| --------------------- | ----------------------------------------------- |
| external_analyzer_arn | ARN of the external access analyzer             |
| external_analyzer_id  | ID of the external access analyzer              |
| unused_analyzer_arn   | ARN of the unused access analyzer (if enabled)  |
| unused_analyzer_id    | ID of the unused access analyzer (if enabled)   |
| account_id            | AWS account ID where Access Analyzer is enabled |

## What Gets Analyzed

IAM Access Analyzer monitors these resource types:

- Amazon S3 buckets
- IAM roles
- KMS keys
- Lambda functions and layers
- SQS queues
- Secrets Manager secrets
- SNS topics
- ECR repositories

## Findings

Access Analyzer generates findings when:

- A resource is accessible by an external principal
- IAM permissions haven't been used within the specified timeframe
- Policies grant broader access than necessary

## Integration with Security Hub

Findings are automatically sent to AWS Security Hub if enabled, providing centralized visibility across all security services.

## Cost Considerations

- External access analyzers: No additional charge
- Unused access analyzers: Charged per IAM role/user analyzed per month
- Refer to [IAM Access Analyzer Pricing](https://aws.amazon.com/iam/access-analyzer/pricing/)

## Notes

- Organization-level analyzers require AWS Organizations to be enabled
- The delegated administrator account must enable the analyzer
- Findings are generated within 30 minutes of policy changes
- Archive rules can be created to suppress expected findings
