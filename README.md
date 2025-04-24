# 🛡️ AWS Security Baseline with Terraform

A modular Terraform implementation to bootstrap security best practices in AWS environments.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Terraform](https://img.shields.io/badge/Terraform-Modules-blueviolet)](https://www.terraform.io/)
[![Super-Linter](https://github.com/jsredmond/aws-security-baseline/actions/workflows/super-linter.yml/badge.svg)](https://github.com/jsredmond/aws-security-baseline/actions/workflows/super-linter.yml)

---

## ✨ Features

| 🔐 Feature   | ✅ Description                      |
| ------------ | ----------------------------------- |
| CloudTrail   | Centralized API logging             |
| Config       | Configuration change tracking       |
| GuardDuty    | Detects threats and provides alerts |
| Detective    | Visual investigation of findings    |
| Security Hub | Central dashboard for findings      |

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
- `variables.tf` – Defines input variables for flexible deployment.
- `cloudtrail.tf` – Sets up CloudTrail logging with multi-region & KMS.
- `config.tf` – Enables AWS Config and sets roles and delivery channels.
- `detective.tf` – Enables Amazon Detective for the account and region.
- `guardduty.tf` – Enables Amazon GuardDuty with the proper config.
- `securityhub.tf` – Enables Security Hub with base + CIS standard checks.
- `random.tf` – Uses random IDs to ensure resource name uniqueness.
- `outputs.tf` – Provides output values for resource identifiers.

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

- ✅ Log lifecycle expiration policies (`CKV_AWS_300`)
- ✅ S3 event notification (`CKV2_AWS_62`)
- ⏭️ Skip: `CKV_AWS_33` – wildcard principal in KMS key allowed for flexibility

Additional notes:

- GuardDuty is enabled with auto-enrollment for all org accounts.  
  (Requires delegated admin.)
- Some checks need manual remediation or org-level setup.

---

## 🛠️ Contributing

We welcome issues and PRs. Open an issue first before submitting large changes.
Contributions should follow best practices and include appropriate testing.

---

## 👤 Author

Maintained by  
[Jeremy Redmond](https://github.com/jsredmond)

---

## 📄 License

This project is licensed under the MIT License – see the
[LICENSE](LICENSE) file for details.
