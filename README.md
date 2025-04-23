# Overview

This project provides a modular Terraform implementation to deploy a
foundational set of AWS security services. It is intended as a baseline
for small to medium-sized AWS environments looking to enforce security
best practices with minimal manual configuration.

The following AWS services are configured and enabled as part of the baseline:

- **AWS CloudTrail** – Centralized logging of all API calls across the account.
- **AWS Config** – Configuration tracking and compliance recording for AWS resources.
- **Amazon Detective** – Visualization and analysis of security findings.
- **Amazon GuardDuty** – Continuous threat detection and anomaly monitoring.
- **AWS Security Hub** – Aggregates security findings and compliance statuses.

## Deploying an AWS Security Baseline with Terraform

[![Super-Linter Status](https://github.com/jsredmond/aws-security-baseline/actions/workflows/super-linter.yml/badge.svg)](https://github.com/jsredmond/aws-security-baseline/actions/workflows/linter.yml)

## Terraform Modules and Files

The configuration is broken into the following key files:

- `providers.tf` – Sets up the AWS provider and region.
- `variables.tf` – Defines reusable input variables for flexible deployment.
- `cloudtrail.tf` – Configures a multi-region CloudTrail trail  
  with an associated S3  
  bucket and encryption.
- `config.tf` – Enables AWS Config, sets up delivery channels, and assigns appropriate
  IAM roles.
- `detective.tf` – Enables Amazon Detective for the account and region.
- `guardduty.tf` – Enables Amazon GuardDuty and sets the appropriate configurations.
- `securityhub.tf` – Activates AWS Security Hub and enables foundational and CIS
  standard checks.
- `random.tf` – Generates random IDs for naming to ensure uniqueness across resource
  deployments.

## Prerequisites

- Terraform >= 1.14.4
  (ensure your local environment meets this version or higher)
- Valid AWS credentials
- Administrator access to the AWS account
- Permissions to enable service-linked roles and create global services like CloudTrail

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/jsredmond/aws-security-baseline.git
   cd aws-security-baseline
   ```

2. Initialize Terraform:

   ```bash
   terraform init
   ```

3. Review and apply the plan:

   ```bash
   terraform plan
   terraform apply
   ```

## Outputs

The Terraform configuration provides the following outputs after deployment:

- `cloudtrail_bucket_name`: Name of the S3 bucket used for CloudTrail logs.
- `config_recorder_name`: Name of the AWS Config recorder.
- `securityhub_account_arn`: ARN of the AWS Security Hub account.
- `guardduty_detector_id`: ID of the GuardDuty detector.
- `detective_graph_id`: ID of the Amazon Detective graph.

## Resources and Documentation

Learn more about the AWS services deployed as part of this security baseline:

- [AWS CloudTrail](https://aws.amazon.com/cloudtrail/)
- [AWS Config](https://aws.amazon.com/config/)
- [Amazon Detective](https://aws.amazon.com/detective/)
- [Amazon GuardDuty](https://aws.amazon.com/guardduty/)
- [AWS Security Hub](https://aws.amazon.com/security-hub/)

## Notes

- This project assumes a single-account setup. For multi-account deployments,
  additional configuration is required.
- Security Hub is enabled with foundational and CIS standard compliance checks.
- All regions are not enabled by default. Ensure `region` is configured as needed.

## Linting and Security Considerations

- **Checkov Policy Skips**:  
  This baseline includes a justified `checkov:skip` directive on
  `CKV_AWS_33` (wildcard principal in KMS key policy) for the
  `aws_kms_key.config_key` resource. This key is used internally, and access
  is tightly scoped in practice, though the wildcard is necessary to meet
  other configuration constraints.

- **GuardDuty Organization Support**:  
  GuardDuty is now enabled with support for auto-enrollment of **all**
  organization accounts. This change requires that the account using this
  Terraform code is assigned as the **GuardDuty delegated administrator** for
  the AWS Organization.

- **S3 Event Notifications and Lifecycle Configuration**:  
  S3 buckets now include lifecycle rules (e.g., log expiration) and event
  notification support using `aws_s3_bucket_notification` where applicable.
  These changes satisfy several security checks including:

  - Lifecycle expiration on logs
    (`CKV_AWS_300`)
  - S3 event notification configuration
    (`CKV2_AWS_62`)
  - Lifecycle configuration existence
    (`CKV2_AWS_61`)

- **Known Tooling Gaps**:  
  Some security checks (e.g., GuardDuty regional enforcement `CKV2_AWS_3`)
  require additional context not enforceable solely through Terraform or are
  constrained by organizational configuration scope. These are being tracked
  and may require manual remediation or future updates to the Terraform
  provider.

## Authors

Repository managed by [Jeremy Redmond](https://github.com/jsredmond).

## License

MIT Licensed. See LICENSE for full details.
