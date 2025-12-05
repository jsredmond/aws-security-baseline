# Amazon Macie Terraform Module

This module enables Amazon Macie for automated sensitive data discovery and protection in Amazon S3.

## Purpose

Amazon Macie uses machine learning to:
- Discover sensitive data in S3 buckets (PII, financial data, credentials)
- Monitor S3 buckets for security and access control issues
- Provide visibility into data security posture
- Generate findings for sensitive data exposure

## Features

- **Automated Discovery**: Continuously monitors S3 for sensitive data
- **Built-in Data Identifiers**: Detects PII, financial data, credentials
- **Custom Identifiers**: Define custom patterns for proprietary data
- **Security Monitoring**: Identifies bucket misconfigurations
- **Security Hub Integration**: Sends findings to Security Hub

## Usage

### Basic Configuration

```hcl
module "macie" {
  source = "./modules/macie"

  environment = "prod"

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### Custom Finding Frequency

```hcl
module "macie" {
  source = "./modules/macie"

  environment                  = "prod"
  finding_publishing_frequency = "FIFTEEN_MINUTES"

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.14.1 |
| aws | >= 6.25.0 |
| random | >= 3.7.2 |

## Providers

| Name | Version |
|------|---------|
| aws | >= 6.25.0 |
| random | >= 3.7.2 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| environment | Environment name (dev, staging, prod) | `string` | n/a | yes |
| finding_publishing_frequency | Frequency of publishing findings | `string` | `"SIX_HOURS"` | no |
| common_tags | Common tags to apply to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| macie_account_id | The unique identifier for the Macie account |
| service_role_arn | ARN of the service-linked role for Macie |
| created_at | Timestamp when Macie was enabled |
| account_id | AWS account ID where Macie is enabled |

## What Macie Detects

### Managed Data Identifiers (Built-in)
- **Personal Information**: Names, addresses, phone numbers, email addresses
- **Financial Data**: Credit card numbers, bank account numbers
- **Credentials**: AWS secret keys, private keys, API keys
- **Health Information**: Medical record numbers, health insurance IDs
- **Geographic Data**: IP addresses, GPS coordinates

### Security Issues
- Unencrypted buckets
- Publicly accessible buckets
- Buckets shared with external accounts
- Buckets without versioning
- Buckets without logging

## Classification Jobs

After enabling Macie, you can create classification jobs to:
- Scan specific S3 buckets
- Run one-time or scheduled scans
- Define sampling depth (percentage of objects to scan)
- Apply custom data identifiers

## Findings

Macie generates two types of findings:

1. **Policy Findings**: Security or privacy issues with S3 buckets
   - Public access
   - Encryption disabled
   - Replication issues

2. **Sensitive Data Findings**: Discovered sensitive data
   - Type of sensitive data found
   - Location (bucket, object key)
   - Severity based on data type

## Integration

- **Security Hub**: Findings automatically sent
- **EventBridge**: Trigger automated responses
- **S3**: Monitors all buckets in the account
- **Organizations**: Can be managed centrally

## Cost Considerations

Macie pricing includes:
- **Bucket evaluation**: Per bucket per month
- **Object monitoring**: Per GB of data processed
- **Sensitive data discovery**: Per GB scanned

First 30 days include:
- 1,000 buckets evaluated free
- 150 GB of data processed free

Refer to [Amazon Macie Pricing](https://aws.amazon.com/macie/pricing/)

## Best Practices

1. **Start Small**: Begin with a subset of buckets
2. **Use Sampling**: For large datasets, use sampling to reduce costs
3. **Create Allow Lists**: Suppress findings for known safe patterns
4. **Schedule Jobs**: Run during off-peak hours
5. **Review Findings**: Regularly review and remediate findings

## Notes

- Macie automatically creates a service-linked role
- Findings are retained for 90 days
- Custom data identifiers use regex patterns
- Supports multi-account management via Organizations
- Can export findings to S3 for long-term retention
