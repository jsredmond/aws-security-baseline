# 🛡️ AWS Security Baseline with Terraform

A modular Terraform implementation to bootstrap security best practices in AWS environments. This project uses a clean modular architecture with dedicated modules for each AWS security service, making it easy to maintain, test, and reuse.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Terraform](https://img.shields.io/badge/Terraform-Modules-blueviolet)](https://www.terraform.io/)
[![Super-Linter](https://github.com/jsredmond/aws-security-baseline/actions/workflows/super-linter.yml/badge.svg)](https://github.com/jsredmond/aws-security-baseline/actions/workflows/super-linter.yml)

---

## ✨ Features

| 🔐 Feature      | ✅ Description                          | 📚 Module                                          |
| --------------- | --------------------------------------- | -------------------------------------------------- |
| CloudTrail      | Centralized API logging with encryption | [modules/cloudtrail](./modules/cloudtrail)         |
| Config          | Configuration change tracking           | [modules/config](./modules/config)                 |
| GuardDuty       | Threat detection and alerts             | [modules/guardduty](./modules/guardduty)           |
| Detective       | Visual investigation of findings        | [modules/detective](./modules/detective)           |
| Security Hub    | Central dashboard for findings          | [modules/securityhub](./modules/securityhub)       |
| Access Analyzer | IAM policy and resource access analysis | [modules/accessanalyzer](./modules/accessanalyzer) |
| Inspector       | Automated vulnerability scanning        | [modules/inspector](./modules/inspector)           |
| Macie           | Sensitive data discovery and protection | [modules/macie](./modules/macie)                   |

---

## 🏗️ Architecture

This project follows a modular architecture where each AWS security service is encapsulated in its own reusable module:

```text
.
├── main.tf                    # Root module - orchestrates all services
├── backend.tf                 # Remote state configuration (S3 + DynamoDB)
├── providers.tf               # AWS provider configuration
├── variables.tf               # Root-level input variables
├── outputs.tf                 # Aggregated outputs from modules
├── versions.tf                # Terraform and provider version constraints
└── modules/                   # Reusable service modules
    ├── accessanalyzer/       # IAM Access Analyzer module
    ├── cloudtrail/           # CloudTrail logging module
    ├── config/               # AWS Config module
    ├── detective/            # Amazon Detective module
    ├── guardduty/            # GuardDuty threat detection module
    ├── inspector/            # Amazon Inspector module
    ├── macie/                # Amazon Macie module
    └── securityhub/          # Security Hub aggregation module
```

### Module Benefits

- **Maintainability:** Each service is isolated in its own module
- **Reusability:** Modules can be used across multiple projects
- **Testability:** Modules can be tested independently
- **Flexibility:** Enable/disable services with simple flags
- **Best Practices:** Follows Terraform module best practices

---

## 🚀 Quick Start

### Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.14.0
- AWS CLI configured with appropriate credentials
- AWS account with permissions for security services

### Basic Deployment

```bash
# Clone the repository
git clone https://github.com/jsredmond/aws-security-baseline.git
cd aws-security-baseline

# Initialize Terraform (downloads providers and modules)
terraform init

# Review the execution plan
terraform plan

# Deploy the security baseline
terraform apply
```

### Custom Configuration

Create a `terraform.tfvars` file to customize your deployment:

```hcl
# terraform.tfvars
environment = "prod"
aws_region  = "us-east-1"

# Enable/disable services
enable_cloudtrail   = true
enable_config       = true
enable_guardduty    = true
enable_detective    = true
enable_securityhub  = true

# Common tags for all resources
common_tags = {
  Project     = "SecurityBaseline"
  ManagedBy   = "Terraform"
  Environment = "Production"
}
```

Then deploy:

```bash
terraform apply -var-file="terraform.tfvars"
```

---

## 📖 Documentation

### Root Module

The root module orchestrates all security services by calling child modules:

- **`main.tf`** – Module calls for each security service
- **`backend.tf`** – S3 backend configuration with DynamoDB locking
- **`providers.tf`** – AWS provider and region configuration
- **`variables.tf`** – Root-level input variables and enable flags
- **`outputs.tf`** – Aggregated outputs from all modules
- **`versions.tf`** – Terraform and provider version constraints

### Service Modules

Each module is self-contained with its own documentation:

#### [CloudTrail Module](./modules/cloudtrail)

Multi-region API logging with KMS encryption, CloudWatch integration, and SNS notifications.

**Key Features:**

- Multi-region trail configuration
- KMS encryption for logs
- CloudWatch Logs integration
- SNS topic for alerts
- S3 bucket with security best practices

#### [Config Module](./modules/config)

Configuration change tracking and compliance monitoring.

**Key Features:**

- Configuration recorder
- S3 delivery channel
- KMS encryption
- IAM role for Config service
- Global resource recording

#### [GuardDuty Module](./modules/guardduty)

Intelligent threat detection with organization-wide support.

**Key Features:**

- Threat detection across AWS accounts
- S3, Kubernetes, and Malware protection
- Organization auto-enrollment
- Configurable finding frequency

#### [Detective Module](./modules/detective)

Visual investigation and analysis of security findings.

**Key Features:**

- Behavior graph for investigation
- Integration with GuardDuty findings
- Requires 48 hours of GuardDuty data

#### [Security Hub Module](./modules/securityhub)

Centralized security findings dashboard.

**Key Features:**

- Aggregates findings from multiple services
- CIS AWS Foundations Benchmark
- AWS Foundational Security Best Practices
- Optional PCI DSS standard

#### [Access Analyzer Module](./modules/accessanalyzer)

IAM policy and resource access analysis.

**Key Features:**

- External access analyzer for public/cross-account access
- Unused access analyzer for least privilege
- Configurable analysis scope

#### [Inspector Module](./modules/inspector)

Automated vulnerability scanning.

**Key Features:**

- EC2 instance vulnerability scanning
- ECR container image scanning
- Lambda function code scanning

#### [Macie Module](./modules/macie)

Sensitive data discovery and protection.

**Key Features:**

- Automated sensitive data discovery
- S3 bucket security analysis
- Configurable finding frequency

### Input Variables

| Variable             | Description                         | Type   | Default      |
| -------------------- | ----------------------------------- | ------ | ------------ |
| `environment`        | Environment name (dev/staging/prod) | string | **required** |
| `aws_region`         | AWS region for deployment           | string | `us-east-1`  |
| `enable_cloudtrail`  | Enable CloudTrail module            | bool   | `true`       |
| `enable_config`      | Enable AWS Config module            | bool   | `true`       |
| `enable_guardduty`   | Enable GuardDuty module             | bool   | `true`       |
| `enable_detective`   | Enable Detective module             | bool   | `true`       |
| `enable_securityhub` | Enable Security Hub module          | bool   | `true`       |
| `common_tags`        | Common tags for all resources       | map    | `{}`         |

See [variables.tf](./variables.tf) for complete variable documentation.

### Outputs

| Output                    | Description                         |
| ------------------------- | ----------------------------------- |
| `cloudtrail_trail_arn`    | ARN of the CloudTrail trail         |
| `cloudtrail_bucket_name`  | Name of the CloudTrail S3 bucket    |
| `config_recorder_name`    | Name of the AWS Config recorder     |
| `config_bucket_name`      | Name of the Config S3 bucket        |
| `guardduty_detector_id`   | ID of the GuardDuty detector        |
| `detective_graph_id`      | ID of the Amazon Detective graph    |
| `securityhub_account_arn` | ARN of the AWS Security Hub account |

See [outputs.tf](./outputs.tf) for complete output documentation.

---

## 🔧 Backend Configuration

This project supports remote state management using S3 and DynamoDB for state locking. Remote state enables team collaboration and provides state locking to prevent concurrent modifications.

### Why Use Remote State?

- **Team Collaboration:** Multiple team members can work on the same infrastructure
- **State Locking:** Prevents concurrent modifications that could corrupt state
- **State Encryption:** Protects sensitive data in state files
- **State Versioning:** S3 versioning provides state history and rollback capability
- **Centralized Management:** Single source of truth for infrastructure state

### Backend Initialization

#### Option 1: Full Backend Configuration (Recommended)

1. **Create S3 bucket and DynamoDB table** (one-time setup):

   ```bash
   # Set variables
   BUCKET_NAME="your-terraform-state-bucket"
   TABLE_NAME="terraform-state-lock"
   REGION="us-east-1"

   # Create S3 bucket for state
   aws s3 mb s3://${BUCKET_NAME} --region ${REGION}

   # Enable versioning (important for state history)
   aws s3api put-bucket-versioning \
     --bucket ${BUCKET_NAME} \
     --versioning-configuration Status=Enabled

   # Enable encryption
   aws s3api put-bucket-encryption \
     --bucket ${BUCKET_NAME} \
     --server-side-encryption-configuration '{
       "Rules": [{
         "ApplyServerSideEncryptionByDefault": {
           "SSEAlgorithm": "AES256"
         }
       }]
     }'

   # Block public access
   aws s3api put-public-access-block \
     --bucket ${BUCKET_NAME} \
     --public-access-block-configuration \
       BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

   # Create DynamoDB table for locking
   aws dynamodb create-table \
     --table-name ${TABLE_NAME} \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region ${REGION}
   ```

2. **Configure backend** in `backend.tf`:

   ```hcl
   terraform {
     backend "s3" {
       bucket         = "your-terraform-state-bucket"
       key            = "security-baseline/terraform.tfstate"
       region         = "us-east-1"
       encrypt        = true
       dynamodb_table = "terraform-state-lock"
     }
   }
   ```

3. **Initialize Terraform with backend**:
   ```bash
   terraform init
   ```

#### Option 2: Partial Backend Configuration

For better security, use partial configuration to avoid hardcoding values:

1. **Create backend configuration file** `backend-config.hcl`:

   ```hcl
   bucket         = "your-terraform-state-bucket"
   key            = "security-baseline/terraform.tfstate"
   region         = "us-east-1"
   encrypt        = true
   dynamodb_table = "terraform-state-lock"
   ```

2. **Update `backend.tf`** to use partial configuration:

   ```hcl
   terraform {
     backend "s3" {}
   }
   ```

3. **Initialize with backend config file**:

   ```bash
   terraform init -backend-config=backend-config.hcl
   ```

4. **Add to `.gitignore`** to prevent committing sensitive values:
   ```text
   backend-config.hcl
   ```

#### Option 3: Environment-Specific Backends

For multiple environments, use separate state files:

1. **Create environment-specific config files:**

   ```bash
   # backend-prod.hcl
   bucket         = "prod-terraform-state"
   key            = "security-baseline/prod.tfstate"
   region         = "us-east-1"
   encrypt        = true
   dynamodb_table = "prod-terraform-lock"

   # backend-staging.hcl
   bucket         = "staging-terraform-state"
   key            = "security-baseline/staging.tfstate"
   region         = "us-east-1"
   encrypt        = true
   dynamodb_table = "staging-terraform-lock"
   ```

2. **Initialize for specific environment:**

   ```bash
   # Production
   terraform init -backend-config=backend-prod.hcl

   # Staging
   terraform init -backend-config=backend-staging.hcl
   ```

### Migrating Local State to Remote Backend

If you have existing local state and want to migrate to remote backend:

1. **Backup your local state:**

   ```bash
   cp terraform.tfstate terraform.tfstate.backup
   ```

2. **Configure backend** (as shown above)

3. **Initialize and migrate:**

   ```bash
   terraform init
   # Terraform will detect local state and ask if you want to migrate
   # Answer "yes" to copy state to remote backend
   ```

4. **Verify migration:**

   ```bash
   # Check remote state
   terraform state list

   # Verify state is in S3
   aws s3 ls s3://your-terraform-state-bucket/security-baseline/
   ```

5. **Remove local state files** (after verification):
   ```bash
   rm terraform.tfstate
   rm terraform.tfstate.backup
   ```

### Backend State Migration (Modular Structure)

If you're migrating from the monolithic structure to the modular structure with remote backend:

1. **Backup current state:**

   ```bash
   terraform state pull > backup-pre-migration-$(date +%Y%m%d-%H%M%S).tfstate
   ```

2. **Configure remote backend** (as shown above)

3. **Initialize with backend:**

   ```bash
   terraform init
   ```

4. **Follow migration guide:**
   See [MIGRATION.md](./MIGRATION.md) for detailed state migration instructions.

### Backend Configuration Variables

The backend configuration supports these variables:

| Variable         | Description                       | Required |
| ---------------- | --------------------------------- | -------- |
| `bucket`         | S3 bucket name for state storage  | Yes      |
| `key`            | Path to state file within bucket  | Yes      |
| `region`         | AWS region for S3 bucket          | Yes      |
| `encrypt`        | Enable server-side encryption     | Yes      |
| `dynamodb_table` | DynamoDB table for state locking  | Yes      |
| `kms_key_id`     | KMS key for encryption (optional) | No       |
| `profile`        | AWS profile to use (optional)     | No       |
| `role_arn`       | IAM role to assume (optional)     | No       |

### Backend Best Practices

1. **Always enable encryption:** Set `encrypt = true`
2. **Enable S3 versioning:** Provides state history and rollback
3. **Use DynamoDB locking:** Prevents concurrent state modifications
4. **Separate state per environment:** Use different buckets or keys
5. **Restrict S3 bucket access:** Use IAM policies to limit access
6. **Enable S3 bucket logging:** Track access to state files
7. **Regular state backups:** Automate state file backups
8. **Use partial configuration:** Avoid hardcoding sensitive values

### Troubleshooting Backend Issues

**Issue:** `Error: Backend configuration changed`

```bash
# Solution: Reconfigure backend
terraform init -reconfigure
```

**Issue:** `Error: Error acquiring the state lock`

```bash
# Check who has the lock
aws dynamodb get-item \
  --table-name terraform-state-lock \
  --key '{"LockID":{"S":"your-bucket/path/to/state"}}'

# Force unlock (use with caution - ensure no one else is running terraform)
terraform force-unlock <LOCK_ID>
```

**Issue:** `Error: Failed to get existing workspaces`

```bash
# Solution: Verify S3 bucket exists and you have access
aws s3 ls s3://your-terraform-state-bucket/
```

**Issue:** State file not found in S3

```bash
# Solution: Initialize backend first
terraform init

# Or migrate existing local state
terraform init -migrate-state
```

### Backend Security Considerations

1. **S3 Bucket Policies:**

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::ACCOUNT_ID:role/TerraformRole"
         },
         "Action": ["s3:GetObject", "s3:PutObject"],
         "Resource": "arn:aws:s3:::your-terraform-state-bucket/*"
       }
     ]
   }
   ```

2. **DynamoDB Table Policies:**

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::ACCOUNT_ID:role/TerraformRole"
         },
         "Action": [
           "dynamodb:PutItem",
           "dynamodb:GetItem",
           "dynamodb:DeleteItem"
         ],
         "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/terraform-state-lock"
       }
     ]
   }
   ```

3. **Enable MFA Delete** (optional but recommended):
   ```bash
   aws s3api put-bucket-versioning \
     --bucket your-terraform-state-bucket \
     --versioning-configuration Status=Enabled,MFADelete=Enabled \
     --mfa "SERIAL_NUMBER TOKEN"
   ```

---

## 🧪 Testing & Security

### CI/CD Security Pipeline

This project uses a comprehensive security analysis pipeline via GitHub Actions:

| Tool         | Purpose                                  | Workflow           |
| ------------ | ---------------------------------------- | ------------------ |
| Super-Linter | Multi-language linting (Terraform, YAML) | `super-linter.yml` |
| Checkov      | Infrastructure security scanning         | Via Super-Linter   |
| TFLint       | Terraform-specific linting               | Via Super-Linter   |
| Dependabot   | Dependency vulnerability scanning        | `dependabot.yml`   |
| Biome        | JSON formatting validation               | Via Super-Linter   |
| yamllint     | YAML syntax and style checking           | Via Super-Linter   |
| markdownlint | Markdown formatting validation           | Via Super-Linter   |

### Security Best Practices Enforced

- **Action Pinning:** All GitHub Actions are pinned to SHA commits for supply chain security
- **Minimal Permissions:** Workflows use least-privilege permission model
- **Credential Protection:** `persist-credentials: false` on checkout actions
- **Dependency Updates:** Automated via Dependabot with cooldown periods

### Local Security Scanning

Run security scans before deploying:

```bash
# Run Checkov security scan (REQUIRED before commits)
checkov -d . --framework terraform

# Run TFLint
tflint --recursive

# Format all Terraform files
terraform fmt -recursive

# Validate configuration
terraform validate
```

### Checkov Configuration

Some checks are intentionally skipped with documented reasons in `.checkov.yaml`:

- ✅ `CKV_AWS_300` – S3 lifecycle policies configured with abort_incomplete_multipart_upload
- ✅ `CKV_AWS_144` – Cross-region replication not required for single-region audit log storage

---

## 📚 Additional Resources

### AWS Service Documentation

Learn more about the AWS services deployed:

- [AWS CloudTrail](https://aws.amazon.com/cloudtrail/)
- [AWS Config](https://aws.amazon.com/config/)
- [Amazon Detective](https://aws.amazon.com/detective/)
- [Amazon GuardDuty](https://aws.amazon.com/guardduty/)
- [AWS Security Hub](https://aws.amazon.com/security-hub/)

### Terraform Best Practices

This project follows best practices from:

- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Terraform Module Registry](https://registry.terraform.io/)

### Migration Guide

If you're migrating from the monolithic structure to the modular structure, see [MIGRATION.md](./MIGRATION.md) for detailed instructions.

---

## 🔐 Security Considerations

### Organization-Level Features

- **GuardDuty:** Auto-enrollment requires delegated admin account
- **Security Hub:** Organization-wide aggregation requires admin account
- **Detective:** Requires 48 hours of GuardDuty data before enabling

### IAM Permissions Required

Deploying this baseline requires permissions for:

- CloudTrail: Create trails, S3 buckets, KMS keys
- Config: Create recorders, delivery channels, IAM roles
- GuardDuty: Enable detector, configure organization
- Detective: Create graph
- Security Hub: Enable account, subscribe to standards
- S3: Create and configure buckets
- KMS: Create and manage encryption keys
- IAM: Create roles and policies
- SNS: Create topics and policies

### Encryption

All data at rest is encrypted:

- S3 buckets use KMS encryption
- CloudWatch Logs use KMS encryption
- Each service has dedicated KMS keys with rotation enabled

### Network Security

- All S3 buckets block public access
- Bucket policies restrict access to AWS services only
- VPC Flow Logs can be integrated (not included by default)

---

## 🚀 Advanced Usage

### Selective Service Deployment

Enable only specific services:

```hcl
# terraform.tfvars
enable_cloudtrail   = true
enable_config       = true
enable_guardduty    = true
enable_detective    = false  # Disable Detective
enable_securityhub  = false  # Disable Security Hub
```

### Multi-Environment Deployment

Use Terraform workspaces or separate state files:

```bash
# Using workspaces
terraform workspace new prod
terraform workspace new staging
terraform workspace new dev

# Deploy to specific workspace
terraform workspace select prod
terraform apply -var="environment=prod"
```

### Module Reuse

Use individual modules in other projects:

```hcl
module "cloudtrail" {
  source = "git::https://github.com/jsredmond/aws-security-baseline.git//modules/cloudtrail?ref=v1.0.0"

  environment                    = "prod"
  cloudwatch_logs_retention_days = 365
  enable_s3_data_events          = true

  common_tags = {
    Project = "MyProject"
  }
}
```

---

## 🛠️ Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Run tests:** `terraform validate && checkov -d .`
5. **Commit with conventional commits:** `git commit -m "feat(module): description"`
6. **Push to your fork:** `git push origin feature/your-feature`
7. **Open a Pull Request**

### Development Workflow

```bash
# Format code
terraform fmt -recursive

# Validate syntax
terraform validate

# Run security scans
checkov -d . --framework terraform
tflint --recursive

# Run tests
cd test && go test -v
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines (if available).

---

## 📋 Roadmap

Future enhancements:

- [ ] VPC Flow Logs integration
- [ ] Automated compliance reporting
- [ ] Multi-region deployment support
- [ ] Terraform Cloud/Enterprise integration
- [ ] Additional compliance standards (HIPAA, SOC 2)
- [ ] AWS Organizations integration
- [ ] Cross-account security aggregation

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** `Error: Module not installed`

```bash
# Solution: Initialize Terraform
terraform init
```

**Issue:** `Error: Backend configuration changed`

```bash
# Solution: Reconfigure backend
terraform init -reconfigure
```

**Issue:** `Error: Insufficient permissions`

```bash
# Solution: Verify IAM permissions for your AWS credentials
aws sts get-caller-identity
```

**Issue:** Detective fails to enable

```bash
# Solution: GuardDuty must be enabled for 48 hours first
# Disable Detective temporarily:
enable_detective = false
```

For more troubleshooting, see [MIGRATION.md](./MIGRATION.md#troubleshooting).

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/jsredmond/aws-security-baseline/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jsredmond/aws-security-baseline/discussions)
- **Documentation:** See module readmes in `modules/` directory

---

## 👤 Author

Maintained by [Jeremy Redmond](https://github.com/jsredmond)

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- AWS Security Best Practices
- Terraform Module Best Practices
- Open source security community

---

## 📊 Project Status

- ✅ Modular architecture implemented (8 security modules)
- ✅ All modules documented with README files
- ✅ Security scanning integrated (Checkov, TFLint)
- ✅ CI/CD workflows configured (Super-Linter, Dependabot)
- ✅ GitHub Actions pinned to SHA for supply chain security

**Current Version:** 2.0.0 (Modular Architecture)

**Terraform Version:** >= 1.14.0

**AWS Provider Version:** >= 6.24.0

**Security Modules:** CloudTrail, Config, GuardDuty, Detective, Security Hub, Access Analyzer, Inspector, Macie
