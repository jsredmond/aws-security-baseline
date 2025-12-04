# Detective Terraform Module

This module deploys and configures Amazon Detective for security investigation and analysis in AWS environments.

## Purpose

Amazon Detective makes it easy to analyze, investigate, and quickly identify the root cause of potential security issues or suspicious activities. This module:

- Enables Detective graph for security investigation
- Integrates with GuardDuty findings
- Provides visual analysis of security data
- Supports investigation workflows

## Features

- **Automated graph creation**: Deploys Detective behavior graph
- **GuardDuty integration**: Analyzes GuardDuty findings
- **Visual investigation**: Provides interactive visualizations
- **Tagging support**: Apply custom tags to all resources

## Usage

### Basic Configuration

```hcl
module "detective" {
  source = "./modules/detective"

  environment = "prod"

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### Minimal Configuration

```hcl
module "detective" {
  source = "./modules/detective"

  environment = "dev"
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0 |
| aws | >= 5.0 |
| random | >= 3.0 |

## Providers

| Name | Version |
|------|---------|
| aws | >= 5.0 |
| random | >= 3.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| environment | Environment name (dev, staging, prod) | `string` | n/a | yes |
| common_tags | Common tags to apply to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| graph_id | The ID of the Detective graph |
| graph_arn | The ARN of the Detective graph |

## Prerequisites

### AWS Permissions

The following IAM permissions are required to deploy this module:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "detective:CreateGraph",
        "detective:DeleteGraph",
        "detective:ListGraphs",
        "detective:UpdateOrganizationConfiguration",
        "detective:DescribeOrganizationConfiguration",
        "detective:TagResource",
        "detective:UntagResource"
      ],
      "Resource": "*"
    }
  ]
}
```

### GuardDuty Requirement

**IMPORTANT**: Amazon Detective requires at least 48 hours of GuardDuty data before it can be enabled. Ensure GuardDuty has been running for at least 48 hours in the region before deploying this module.

### Service Quotas

- Detective graph: 1 per region per account
- Member accounts: Up to 1,200 per behavior graph

## Data Sources

Detective analyzes data from:

1. **VPC Flow Logs**: Network traffic patterns
2. **CloudTrail Logs**: API activity and user behavior
3. **GuardDuty Findings**: Security findings and alerts

Detective automatically ingests this data once enabled.

## Investigation Capabilities

Detective provides:

- **Finding Groups**: Related findings grouped together
- **Entity Profiles**: Detailed views of AWS resources
- **Time-based Analysis**: Historical behavior patterns
- **Visual Graphs**: Interactive relationship visualizations
- **Scope Time**: Adjustable investigation time windows

## Notes

- Detective requires GuardDuty to be enabled for at least 48 hours
- Data is retained for 1 year in the behavior graph
- Detective automatically processes new data as it arrives
- The service has a 30-day free trial for new accounts
- Organization support requires delegated administrator setup

## Cost Considerations

Detective pricing is based on:

1. **Data Ingestion**: Per GB of data ingested from VPC Flow Logs and CloudTrail
2. **Data Analysis**: Per GB of data analyzed

Pricing tiers:
- First 1 TB/month: Standard rate
- Next 4 TB/month: Reduced rate
- Over 5 TB/month: Further reduced rate

Refer to [AWS Detective Pricing](https://aws.amazon.com/detective/pricing/) for current rates.

## Integration

Detective integrates with:

- **Amazon GuardDuty**: Primary source of security findings
- **AWS Security Hub**: Centralized security findings dashboard
- **Amazon CloudWatch**: Monitoring and alerting
- **AWS IAM**: Access control and permissions

## Troubleshooting

### Graph Creation Fails

- **Verify GuardDuty**: Ensure GuardDuty has been enabled for at least 48 hours
- **Check Permissions**: Verify IAM permissions are correct
- **Regional Availability**: Confirm Detective is available in your region
- **Existing Graph**: Check if a graph already exists in the region

### Insufficient Data Error

- **Wait Period**: Detective requires 48 hours of GuardDuty data
- **GuardDuty Status**: Verify GuardDuty is actively collecting data
- **Data Sources**: Ensure GuardDuty data sources are enabled

### Organization Configuration Issues

- **Delegated Admin**: Verify account is designated as delegated administrator
- **AWS Organizations**: Ensure AWS Organizations is properly configured
- **Member Accounts**: Check member account limits and permissions

## Best Practices

1. **Enable GuardDuty First**: Always enable GuardDuty at least 48 hours before Detective
2. **Organization Deployment**: Use delegated administrator for organization-wide deployment
3. **Regular Reviews**: Periodically review findings and investigation results
4. **Tag Resources**: Use consistent tagging for cost allocation and management
5. **Access Control**: Limit Detective access to security team members

## Investigation Workflow

Typical investigation workflow:

1. **Receive Alert**: GuardDuty finding or Security Hub alert
2. **Open Detective**: Navigate to Detective console
3. **Select Finding**: Choose the finding to investigate
4. **Analyze Graph**: Review entity relationships and behaviors
5. **Adjust Scope**: Modify time window as needed
6. **Document Findings**: Record investigation results
7. **Take Action**: Implement remediation steps

## References

- [Amazon Detective Documentation](https://docs.aws.amazon.com/detective/)
- [Detective User Guide](https://docs.aws.amazon.com/detective/latest/userguide/)
- [Detective Best Practices](https://docs.aws.amazon.com/detective/latest/adminguide/detective-best-practices.html)
- [Investigation Examples](https://docs.aws.amazon.com/detective/latest/userguide/detective-investigation-examples.html)
