<p align="center">
  <img align="center" src="https://img.shields.io/badge/🛡️-AWS_Security_Baseline-blue?style=for-the-badge&labelColor=232F3E" width="50%" height="50%">
</p>

<p align="center">
  <b>AWS Security Baseline</b> is a modular Terraform implementation that bootstraps security best practices in AWS environments. Deploy 8 core security services with a single command using production-ready, reusable modules.
</p>

<p align="center">
  <b>Secure your AWS account in minutes at <a href="https://github.com/jsredmond/aws-security-baseline">github.com/jsredmond/aws-security-baseline</a></b>
</p>

<hr>

<p align="center">
  <a href="https://github.com/jsredmond/aws-security-baseline/actions/workflows/super-linter.yml"><img alt="Super-Linter" src="https://github.com/jsredmond/aws-security-baseline/actions/workflows/super-linter.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://www.terraform.io/"><img alt="Terraform" src="https://img.shields.io/badge/Terraform-%3E%3D1.14.3-blueviolet"></a>
  <a href="https://registry.terraform.io/providers/hashicorp/aws/latest"><img alt="AWS Provider" src="https://img.shields.io/badge/AWS_Provider-%3E%3D6.27-orange"></a>
</p>

<p align="center">
  <a href="https://github.com/jsredmond/aws-security-baseline/releases"><img alt="Release" src="https://img.shields.io/github/v/release/jsredmond/aws-security-baseline"></a>
  <a href="https://github.com/jsredmond/aws-security-baseline/issues"><img alt="Issues" src="https://img.shields.io/github/issues/jsredmond/aws-security-baseline"></a>
  <a href="https://github.com/jsredmond/aws-security-baseline"><img alt="Stars" src="https://img.shields.io/github/stars/jsredmond/aws-security-baseline"></a>
</p>

<hr>

<p align="center">
  <img align="center" src="assets/wizard.png" width="80%" height="80%">
</p>

# Description

**AWS Security Baseline** provides a comprehensive, modular Terraform implementation for deploying core AWS security services. Each service is encapsulated in its own reusable module, following Terraform best practices for maintainability, testability, and flexibility.

The baseline includes ready-to-use modules for:

- **CloudTrail**: Centralized API logging with KMS encryption, CloudWatch integration, and SNS notifications
- **AWS Config**: Configuration change tracking and compliance monitoring
- **GuardDuty**: Intelligent threat detection with organization-wide support
- **Detective**: Visual investigation and analysis of security findings
- **Security Hub**: Centralized security findings dashboard with CIS and AWS Foundational standards
- **IAM Access Analyzer**: External access analysis for public/cross-account access
- **Amazon Inspector**: Automated vulnerability scanning for EC2, ECR, and Lambda
- **Amazon Macie**: Sensitive data discovery and protection

## Deployment Wizard

The **Deployment Wizard** is an interactive CLI tool that simplifies configuration. It guides you through selecting services, configuring regions, and generating `terraform.tfvars` files.

```console
python wizard.py
```

![Wizard Demo](assets/wizard.png)

> For detailed instructions, refer to the [Wizard Documentation](wizard/README.md)

## Quick Start

```console
# Clone and deploy
git clone https://github.com/jsredmond/aws-security-baseline.git
cd aws-security-baseline
terraform init
terraform apply
```

# Security Services at a Glance

| Service | Description | Module | Key Features |
|---------|-------------|--------|--------------|
| CloudTrail | API logging | [modules/cloudtrail](./modules/cloudtrail) | Multi-region, KMS encryption, CloudWatch |
| AWS Config | Change tracking | [modules/config](./modules/config) | Compliance monitoring, S3 delivery |
| GuardDuty | Threat detection | [modules/guardduty](./modules/guardduty) | S3/K8s/Malware protection, Org support |
| Detective | Investigation | [modules/detective](./modules/detective) | Behavior graphs, GuardDuty integration |
| Security Hub | Dashboard | [modules/securityhub](./modules/securityhub) | CIS, AWS Foundational, PCI-DSS |
| Access Analyzer | IAM analysis | [modules/accessanalyzer](./modules/accessanalyzer) | External access, unused access |
| Inspector | Vulnerability scan | [modules/inspector](./modules/inspector) | EC2, ECR, Lambda scanning |
| Macie | Data discovery | [modules/macie](./modules/macie) | Sensitive data, S3 analysis |

# 💻 Installation

## Using the Wizard (Recommended)

**Requirements**

- Python 3.9+
- Terraform >= 1.14.3
- AWS CLI configured

**Commands**

```console
# Install wizard dependencies
python3 -m venv wizard/.venv
source wizard/.venv/bin/activate
pip install -r wizard/requirements.txt

# Run interactive wizard
python wizard.py

# Or use non-interactive mode
python wizard.py --all-modules --region us-east-1 --env production
```

## Manual Configuration

**Requirements**

- Terraform >= 1.14.3
- AWS CLI configured with appropriate permissions

**Commands**

```console
git clone https://github.com/jsredmond/aws-security-baseline.git
cd aws-security-baseline

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit configuration
vim terraform.tfvars

# Deploy
terraform init
terraform plan
terraform apply
```

## Configuration Options

```hcl
# terraform.tfvars
environment = "prod"
aws_region  = "us-east-1"

# Enable/disable services
enable_cloudtrail   = true
enable_config       = true
enable_guardduty    = true
enable_detective    = true   # Requires 48 hours of GuardDuty data
enable_securityhub  = true
enable_accessanalyzer = true
enable_inspector    = true
enable_macie        = true

# Common tags
common_tags = {
  Project     = "SecurityBaseline"
  ManagedBy   = "Terraform"
  Environment = "prod"
}
```

# ✏️ Architecture

```
.
├── main.tf              # Root module - orchestrates all services
├── backend.tf           # Remote state configuration (S3 + DynamoDB)
├── providers.tf         # AWS provider configuration
├── variables.tf         # Root-level input variables
├── outputs.tf           # Aggregated outputs from modules
├── versions.tf          # Terraform and provider version constraints
├── wizard.py            # Deployment wizard entry point
├── wizard/              # Wizard CLI package
└── modules/             # Reusable service modules
    ├── accessanalyzer/
    ├── cloudtrail/
    ├── config/
    ├── detective/
    ├── guardduty/
    ├── inspector/
    ├── macie/
    └── securityhub/
```

## Module Structure

Each module follows Terraform best practices:

```
modules/<service>/
├── main.tf          # Primary resources
├── variables.tf     # Input variables
├── outputs.tf       # Output values
├── versions.tf      # Provider requirements
└── README.md        # Documentation
```

# 🔐 Security Features

- **Encryption**: All data at rest encrypted with KMS (key rotation enabled)
- **Access Control**: S3 buckets block public access
- **Logging**: Comprehensive audit logging via CloudTrail
- **Compliance**: Security Hub integrates CIS and AWS Foundational standards
- **Organization Support**: GuardDuty auto-enrollment for organization accounts

# 📖 Documentation

For detailed instructions, usage examples, and module documentation:

- [Deployment Testing Guide](./DEPLOYMENT_TEST.md)
- [Wizard Documentation](./wizard/README.md)
- [Security Policy](./SECURITY.md)

**Module Documentation:**

- [CloudTrail](./modules/cloudtrail/README.md) | [Config](./modules/config/README.md) | [GuardDuty](./modules/guardduty/README.md) | [Detective](./modules/detective/README.md)
- [Security Hub](./modules/securityhub/README.md) | [Access Analyzer](./modules/accessanalyzer/README.md) | [Inspector](./modules/inspector/README.md) | [Macie](./modules/macie/README.md)

# 📃 License

AWS Security Baseline is licensed under the MIT License.

A copy of the License is available at [LICENSE](LICENSE)
