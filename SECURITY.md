# 🔐 Security Policy

## 🛡️ Software Security Practices

This repository is maintained as part of Heliobright's commitment to  
secure-by-default infrastructure design. We follow best practices for  
infrastructure-as-code (IaC) security and apply automated scanning tools to  
ensure code and configuration safety.

### ✅ Continuous Security Tools

We utilize the following tools as part of our continuous validation pipeline:

- [**Super-Linter**](https://github.com/github/super-linter): Scans for  
  errors and bad practices across:
  - `terraform`, `markdown`, `yaml`, `github_actions`, and more.
- **Checkov**: Validates Terraform security misconfigurations and compliance
  against AWS best practices.
- **TFLint** and **Terraform FMT**: Enforce consistent, error-free  
  Terraform formatting and linting.
- **Terrascan**: Scans for violations against known security policies in IaC  
  templates.
- **Secret scanning and code scanning**: Enabled via GitHub security settings.

Security scanning is executed automatically via GitHub Actions for every PR  
to `main` and on a scheduled weekly basis.

---

## 📦 Supported Versions

We provide security support for the latest version of the `main` branch only:

| Version         | Supported |
| --------------- | --------- |
| `main` (latest) | ✅        |
| Older versions  | ❌        |

---

## 📢 Reporting a Vulnerability

We take security seriously and welcome reports from the community.

If you discover a potential vulnerability:

- **Where to report**:  
  Open a GitHub [security advisory](https://github.com/jsredmond/aws-security-baseline/security/advisories/new)
  to initiate a private discussion with the maintainers.
- **What to include**:
  - Provide a clear description  
    of the issue
  - Affected modules or files
  - Reproduction steps, if applicable

We will acknowledge receipt within **3 business days**, triage the report,  
and work with you on coordinated disclosure if required.

---

## 🤝 Coordinated Disclosure Policy

We adhere to coordinated disclosure practices. If the vulnerability impacts  
downstream consumers, we will collaborate on a responsible communication and  
remediation timeline prior to public disclosure.

---

Thanks for contributing to a safer cloud ecosystem!
