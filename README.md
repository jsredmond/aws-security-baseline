# Overview

This project provides a modular Terraform implementation to deploy a foundational set of AWS security services. It is intended as a baseline for small to medium-sized AWS environments looking to enforce security best practices with minimal manual configuration.

The following AWS services are configured and enabled as part of the baseline:

- **AWS CloudTrail** – Centralized logging of all API calls across the account.
- **AWS Config** – Configuration tracking and compliance recording for AWS resources.
- **Amazon Detective** – Visualization and analysis of security findings.
- **Amazon GuardDuty** – Continuous threat detection and anomaly monitoring.
- **AWS Security Hub** – Aggregation of security alerts and compliance status across services.

# Deploying an AWS Security Baseline with Terraform

[![Super-Linter](https://github.com/jsredmond/aws-security-baseline/actions/workflows/linter.yml/badge.svg)](https://github.com/jsredmond/aws-security-baseline/actions/workflows/linter.yml)

## Terraform Modules and Files

The configuration is broken into the following key files:

- `providers.tf` – Sets up the AWS provider and region.
- `variables.tf` – Defines reusable input variables for flexible deployment.
- `cloudtrail.tf` – Configures a multi-region CloudTrail trail with an associated S3 bucket and encryption.
- `config.tf` – Enables AWS Config, sets up delivery channels, and assigns appropriate IAM roles.
- `detective.tf` – Enables Amazon Detective for the account and region.
- `guardduty.tf` – Enables Amazon GuardDuty and sets the appropriate configurations.
- `securityhub.tf` – Activates AWS Security Hub and enables foundational and CIS standard checks.
- `random.tf` – Generates random IDs for naming to ensure uniqueness across resource deployments.

## Prerequisites

- Terraform >= 1.14.4
- Valid AWS credentials
- Administrator access to the AWS account
- Permissions to enable service-linked roles and create global services like CloudTrail

## Usage

1. Clone the repository:
   ```
   git clone https://github.com/jsredmond/aws-security-baseline.git
   cd aws-security-baseline
   ```

2. Initialize Terraform:
   ```
   terraform init
   ```

3. Review and apply the plan:
   ```
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

- This project assumes a single-account setup. For multi-account deployments, additional configuration is required.
- Security Hub is enabled with foundational and CIS standard compliance checks.
- All regions are not enabled by default. Ensure `region` is configured as needed.

## Authors

Repository managed by [Jeremy Redmond](https://github.com/jsredmond).

## License

MIT Licensed. See LICENSE for full details.