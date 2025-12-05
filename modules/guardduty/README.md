# GuardDuty Terraform Module

This module deploys and configures Amazon GuardDuty for threat detection and continuous security monitoring in AWS environments.

## Purpose

Amazon GuardDuty is a threat detection service that continuously monitors for malicious activity and unauthorized behavior. This module:

- Enables GuardDuty detector with configurable data sources
- Configures S3 protection, Kubernetes audit logs, and malware protection
- Supports organization-wide deployment with auto-enrollment
- Provides flexible finding notification frequency

## Features

- **Multi-source threat detection**: S3, Kubernetes, and EC2 malware scanning
- **Organization support**: Auto-enable for new organization members
- **Configurable notifications**: Control finding update frequency
- **Flexible data sources**: Enable/disable specific protection types
- **Tagging support**: Apply custom tags to all resources

## Usage

### Standalone Account

```hcl
module "guardduty" {
  source = "./modules/guardduty"

  environment                   = "prod"
  finding_publishing_frequency  = "SIX_HOURS"
  enable_s3_logs               = true
  enable_kubernetes_logs       = true
  enable_malware_protection    = true
  is_organization_admin_account = false

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### Organization Admin Account

```hcl
module "guardduty" {
  source = "./modules/guardduty"

  environment                      = "prod"
  finding_publishing_frequency     = "ONE_HOUR"
  enable_s3_logs                  = true
  enable_kubernetes_logs          = true
  enable_malware_protection       = true
  is_organization_admin_account    = true
  auto_enable_organization_members = "NEW"

  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### Minimal Configuration

```hcl
module "guardduty" {
  source = "./modules/guardduty"

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
| finding_publishing_frequency | Frequency of notifications about updated findings (FIFTEEN_MINUTES, ONE_HOUR, SIX_HOURS) | `string` | `"SIX_HOURS"` | no |
| enable_s3_logs | Enable S3 protection data source | `bool` | `true` | no |
| enable_kubernetes_logs | Enable Kubernetes audit logs data source | `bool` | `true` | no |
| enable_malware_protection | Enable malware protection for EC2 instances | `bool` | `true` | no |
| auto_enable_organization_members | Auto-enable GuardDuty for organization members (ALL, NEW, NONE) | `string` | `"NEW"` | no |
| is_organization_admin_account | Whether this account is the GuardDuty delegated administrator for the organization | `bool` | `false` | no |
| common_tags | Common tags to apply to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| detector_id | The ID of the GuardDuty detector |
| detector_arn | The ARN of the GuardDuty detector |
| account_id | The AWS account ID where GuardDuty is enabled |

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
        "guardduty:CreateDetector",
        "guardduty:UpdateDetector",
        "guardduty:DeleteDetector",
        "guardduty:GetDetector",
        "guardduty:ListDetectors",
        "guardduty:TagResource",
        "guardduty:UntagResource",
        "guardduty:UpdateOrganizationConfiguration",
        "guardduty:DescribeOrganizationConfiguration"
      ],
      "Resource": "*"
    }
  ]
}
```

### Organization Configuration

For organization-wide deployment:

1. **Delegated Administrator**: The account must be designated as the GuardDuty delegated administrator
2. **AWS Organizations**: Must have AWS Organizations enabled
3. **Service-Linked Role**: GuardDuty service-linked role will be created automatically

### Service Quotas

- GuardDuty detector: 1 per region per account
- Member accounts: Up to 5,000 per organization

## Recent Security Enhancements

This module has been updated to enable additional GuardDuty protection plans:

1. **Runtime Monitoring**: Monitors operating system-level events on EC2 instances, EKS clusters, and ECS Fargate tasks
   - Automated agent management for EC2, EKS, and ECS Fargate
   - Detects runtime threats like malware, unauthorized access, and suspicious behavior
   
2. **Lambda Protection**: Monitors Lambda network activity logs
   - Detects threats to Lambda functions including cryptomining and data exfiltration
   - Essential for serverless workload security

3. **RDS Protection**: Analyzes RDS login activity
   - Detects anomalous login patterns and brute force attacks
   - Critical for database security monitoring

4. **EKS Runtime Monitoring**: Enhanced EKS threat detection
   - Monitors both control plane (audit logs) and data plane (runtime) activities
   - Enables detection of multi-stage attacks across EKS layers

These enhancements provide:
- Deeper visibility into workload security across compute types
- Detection of runtime threats that foundational data sources miss
- Comprehensive coverage for modern cloud-native architectures

## Data Sources

GuardDuty monitors the following data sources:

1. **VPC Flow Logs**: Network traffic analysis (always enabled)
2. **DNS Logs**: DNS query analysis (always enabled)
3. **CloudTrail Events**: API call monitoring (always enabled)
4. **S3 Data Events**: S3 bucket activity (configurable)
5. **Kubernetes Audit Logs**: EKS cluster activity (configurable)
6. **Malware Protection**: EC2 instance scanning (configurable)
7. **Runtime Monitoring**: OS-level events on EC2, EKS, ECS (enabled)
8. **Lambda Protection**: Lambda network activity (enabled)
9. **RDS Protection**: RDS login activity (enabled)
10. **EKS Runtime Monitoring**: Enhanced EKS monitoring (enabled)

## Finding Publishing Frequency

Controls how often GuardDuty publishes updated findings:

- `FIFTEEN_MINUTES`: Most frequent, higher costs
- `ONE_HOUR`: Balanced frequency
- `SIX_HOURS`: Default, cost-effective

## Notes

- GuardDuty has a 30-day free trial for new accounts
- Findings are retained for 90 days
- Organization configuration requires delegated administrator setup
- Malware protection incurs additional costs for EBS volume scans
- S3 protection monitors CloudTrail S3 data events

## Cost Considerations

GuardDuty pricing is based on:

1. **CloudTrail Events**: Per million events analyzed
2. **VPC Flow Logs**: Per GB analyzed
3. **DNS Logs**: Per million queries analyzed
4. **S3 Logs**: Per million events analyzed
5. **Kubernetes Logs**: Per GB analyzed
6. **Malware Protection**: Per GB scanned

Refer to [AWS GuardDuty Pricing](https://aws.amazon.com/guardduty/pricing/) for current rates.

## Integration

GuardDuty findings can be integrated with:

- **AWS Security Hub**: Centralized security findings
- **Amazon Detective**: Investigation and analysis
- **Amazon EventBridge**: Automated response workflows
- **AWS Lambda**: Custom remediation actions
- **SNS/SQS**: Notification systems

## Troubleshooting

### Detector Not Creating

- Verify IAM permissions
- Check if detector already exists in the region
- Ensure AWS Organizations is properly configured (for org accounts)

### Organization Configuration Failing

- Verify account is delegated administrator
- Check AWS Organizations is enabled
- Ensure proper cross-account permissions

### Data Sources Not Enabling

- Verify service quotas
- Check regional availability of features
- Ensure proper IAM permissions for data source access

## References

- [Amazon GuardDuty Documentation](https://docs.aws.amazon.com/guardduty/)
- [GuardDuty Best Practices](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_best-practices.html)
- [GuardDuty Findings](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings.html)
