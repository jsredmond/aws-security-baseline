# 🛡️ AWS Security Baseline with Terraform

A modular Terraform implementation to bootstrap security best practices in AWS environments.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Terraform](https://img.shields.io/badge/Terraform-Modules-blueviolet)](https://www.terraform.io/)

---

## ✨ Features

| 🔐 Feature   | ✅ Description                   |
| ------------ | -------------------------------- |
| CloudTrail   | Centralized API logging          |
| Config       | Configuration change tracking    |
| GuardDuty    | Threat detection & alerts        |
| Detective    | Visual investigation of findings |
| Security Hub | Central dashboard for findings   |

---

## 🚀 Getting Started

```bash
git clone https://github.com/jsredmond/aws-security-baseline.git
cd aws-security-baseline
terraform init
terraform plan
terraform apply
```

---

## 📖 Documentation

### Terraform Modules and Files

- `providers.tf` – Sets up the AWS provider and region.
- `variables.tf` – Defines reusable input variables for flexible deployment.
- `cloudtrail.tf` – Configures a multi-region CloudTrail trail with an associated S3 bucket and
  encryption.
- `config.tf` – Enables AWS Config, sets up delivery channels, and assigns appropriate IAM roles.
- `detective.tf` – Enables Amazon Detective for the account and region.
- `guardduty.tf` – Enables Amazon GuardDuty and sets the appropriate configurations.
- `securityhub.tf` – Activates AWS Security Hub and enables foundational and CIS standard checks.
- `random.tf` – Generates random IDs for naming to ensure uniqueness across resource deployments.

### Outputs

- `cloudtrail_bucket_name`: Name of the S3 bucket used for CloudTrail logs.
- `config_recorder_name`: Name of the AWS Config recorder.
- `securityhub_account_arn`: ARN of the AWS Security Hub account.
- `guardduty_detector_id`: ID of the GuardDuty detector.
- `detective_graph_id`: ID of the Amazon Detective graph.

### Resources

Learn more about the AWS services deployed as part of this security baseline:

- [AWS CloudTrail](https://aws.amazon.com/cloudtrail/)
- [AWS Config](https://aws.amazon.com/config/)
- [Amazon Detective](https://aws.amazon.com/detective/)
- [Amazon GuardDuty](https://aws.amazon.com/guardduty/)
- [AWS Security Hub](https://aws.amazon.com/security-hub/)

---

## 🧪 Linting & Security

Includes Checkov, TFLint, and Terrascan integration.

- ✅ Lifecycle policies for logs expiration (`CKV_AWS_300`)
- ✅ S3 notification setup (`CKV2_AWS_62`)
- ⏭️ Skips: `CKV_AWS_33` (wildcard principal in KMS key policy) with justification

Additional notes:

- GuardDuty is enabled with auto-enrollment for all organization accounts (requires delegated
  admin).
- Some checks require manual remediation or organizational setup due to tooling limitations.

---

## 🛠️ Contributing

We welcome issues and PRs! Please open an issue before submitting major changes.  
Contributions should follow best practices and include appropriate testing.

---

## 👤 Author

Maintained by [Jeremy Redmond](https://github.com/jsredmond)

---

## 📄 License

This project is licensed under the MIT License – see the
[LICENSE](LICENSE) file for details.
