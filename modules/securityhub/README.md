# AWS Security Hub Terraform Module

This module deploys and configures AWS Security Hub for centralized security findings and compliance monitoring.

## Purpose

AWS Security Hub provides a comprehensive view of security alerts and compliance status across AWS accounts. This module enables Security Hub and optionally subscribes to security standards including CIS AWS Foundations Benchmark, PCI DSS, and AWS Foundational Security Best Practices.

## Features

- Enables AWS Security Hub in the specified region
- Optional subscription to CIS AWS Foundations Benchmark v1.4.0
- Optional subscription to PCI DSS v3.2.1
- Optional subscription to AWS Foundational Security Best Practices v1.0.0
- Product integrations with GuardDuty, Inspector, and Macie
- Control finding generator to reduce duplicate findings
- Auto-enable controls for new security checks
- Configurable standards based on compliance requirements
- Consistent tagging across all resources

## Recent Security Enhancements

This module has been updated to implement AWS Security Hub best practices:

1. **Control Finding Generator**: Set to `SECURITY_CONTROL` to consolidate findings
   - Reduces duplicate findings from multiple standards
   - Provides cleaner, more actionable security dashboard
   - Improves finding prioritization and remediation workflow

2. **Auto-Enable Controls**: Automatically enables new security controls as they're released
   - Ensures continuous security coverage
   - Reduces manual configuration overhead
   - Keeps security posture current with AWS recommendations

3. **Product Integrations**: Added support for GuardDuty, Inspector, and Macie integrations
   - Aggregates findings from multiple AWS security services
   - Provides centralized security findings dashboard
   - Enables comprehensive security monitoring

These enhancements provide:

- Reduced finding noise and improved signal-to-noise ratio
- Automatic adoption of new security controls
- Comprehensive security findings aggregation
- Better security posture visibility

## Usage

### Basic Example

```hcl
module "securityhub" {
  source = "./modules/securityhub"
}
```

### Custom Standards Configuration

```hcl
module "securityhub" {
  source = "./modules/securityhub"

  # Enable only specific standards
  enable_cis_standard              = true
  enable_pci_dss_standard          = true
  enable_aws_foundational_standard = false

  # Enable product integrations
  enable_guardduty_integration     = true
  enable_inspector_integration     = true
  enable_macie_integration         = false
}
```

### Development Environment

```hcl
module "securityhub" {
  source = "./modules/securityhub"

  # Enable only AWS Foundational standard for dev
  enable_cis_standard              = false
  enable_pci_dss_standard          = false
  enable_aws_foundational_standard = true
}
```

## Requirements

| Name      | Version   |
| --------- | --------- |
| terraform | >= 1.14.0 |
| aws       | >= 6.24.0 |

## Providers

| Name | Version   |
| ---- | --------- |
| aws  | >= 6.24.0 |

## Resources

| Name                                             | Type        |
| ------------------------------------------------ | ----------- |
| aws_securityhub_account.main                     | resource    |
| aws_securityhub_standards_subscription.standards | resource    |
| aws_caller_identity.current                      | data source |
| aws_region.current                               | data source |

## Inputs

| Name                             | Description                                              | Type   | Default | Required |
| -------------------------------- | -------------------------------------------------------- | ------ | ------- | :------: |
| enable_cis_standard              | Enable CIS AWS Foundations Benchmark standard            | `bool` | `true`  |    no    |
| enable_pci_dss_standard          | Enable PCI DSS standard                                  | `bool` | `false` |    no    |
| enable_aws_foundational_standard | Enable AWS Foundational Security Best Practices standard | `bool` | `true`  |    no    |
| enable_guardduty_integration     | Enable GuardDuty product integration with Security Hub   | `bool` | `true`  |    no    |
| enable_inspector_integration     | Enable Inspector product integration with Security Hub   | `bool` | `true`  |    no    |
| enable_macie_integration         | Enable Macie product integration with Security Hub       | `bool` | `false` |    no    |

## Outputs

| Name                    | Description                                     |
| ----------------------- | ----------------------------------------------- |
| account_arn             | ARN of the Security Hub account                 |
| account_id              | ID of the Security Hub account                  |
| enabled_standards       | Map of enabled Security Hub standards           |
| standards_subscriptions | Map of Security Hub standards subscription ARNs |

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
        "securityhub:EnableSecurityHub",
        "securityhub:DisableSecurityHub",
        "securityhub:DescribeHub",
        "securityhub:UpdateSecurityHubConfiguration",
        "securityhub:BatchEnableStandards",
        "securityhub:BatchDisableStandards",
        "securityhub:GetEnabledStandards",
        "securityhub:DescribeStandards",
        "securityhub:TagResource",
        "securityhub:UntagResource",
        "securityhub:ListTagsForResource"
      ],
      "Resource": "*"
    }
  ]
}
```

### Service Prerequisites

- AWS account must have Security Hub available in the region
- For organization-wide deployment, the account should be the Security Hub administrator account
- GuardDuty, Config, and other security services should be enabled for comprehensive findings

### Service Quotas

- Security Hub is available in most AWS regions
- Check [AWS Security Hub endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/securityhub.html) for region availability

## Security Standards

### CIS AWS Foundations Benchmark v1.4.0

The CIS AWS Foundations Benchmark provides prescriptive guidance for configuring security options for AWS. It includes recommendations for:

- Identity and Access Management
- Logging and Monitoring
- Networking
- Data Protection

**Enabled by default**: Yes

### PCI DSS v3.2.1

The Payment Card Industry Data Security Standard (PCI DSS) is an information security standard for organizations that handle credit cards. This standard includes requirements for:

- Network Security
- Access Control
- Data Protection
- Monitoring and Testing

**Enabled by default**: No (enable only if handling payment card data)

### AWS Foundational Security Best Practices v1.0.0

AWS Foundational Security Best Practices standard is a set of controls that detect when deployed AWS accounts and resources deviate from security best practices. It covers:

- AWS service configurations
- Security best practices
- Compliance requirements

**Enabled by default**: Yes

## Integration with Other Services

Security Hub aggregates findings from:

- AWS GuardDuty (threat detection)
- AWS Config (configuration compliance)
- AWS Inspector (vulnerability assessment)
- AWS Macie (data security)
- AWS Firewall Manager (firewall management)
- Third-party security products

## Notes

- Security Hub must be enabled in each region where you want to aggregate findings
- Standards subscriptions are region-specific
- Disabling Security Hub will remove all findings and configurations
- Standards can be enabled or disabled independently
- Some standards may generate findings that require remediation
- Review findings regularly and implement recommended remediations

## Compliance Considerations

- CIS Benchmark is commonly required for compliance frameworks
- PCI DSS is required for organizations handling payment card data
- AWS Foundational Best Practices align with AWS Well-Architected Framework
- Regular review of findings is essential for maintaining compliance
- Document any suppressed findings with business justification

## Cost Considerations

Security Hub pricing includes:

- Per security check per month
- Per finding ingestion event per month
- Costs vary by region

Enable only the standards you need to optimize costs. For development environments, consider enabling only AWS Foundational Best Practices.

## Troubleshooting

### Security Hub Already Enabled

If Security Hub is already enabled in the account/region:

```bash
terraform import module.securityhub.aws_securityhub_account.main <account-id>
```

### Standards Subscription Errors

If standards subscription fails:

1. Verify Security Hub is enabled
2. Check that the standard is available in your region
3. Ensure you have the required IAM permissions

### Findings Not Appearing

If findings are not appearing:

1. Verify that source services (GuardDuty, Config) are enabled
2. Check that Security Hub has the necessary permissions
3. Allow time for initial findings to populate (can take several hours)

## References

- [AWS Security Hub Documentation](https://docs.aws.amazon.com/securityhub/)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
- [AWS Foundational Security Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-standards-fsbp.html)
