# GitHub Configuration

## Security Scanning

### CodeQL

CodeQL is **disabled** for this repository because:

- This is primarily a **Terraform (HCL)** project
- CodeQL does not support Terraform/HCL analysis
- The minimal Python code (audit scripts) is better covered by other tools

### Active Security Tools

Instead of CodeQL, this project uses:

1. **Checkov** - Terraform security scanning
   - Scans for security misconfigurations
   - Validates against AWS best practices
   - Required to pass before commits

2. **Super-Linter** - Multi-language linting
   - Configured in `.github/workflows/super-linter.yml`
   - Validates Terraform, Python, YAML, and more

3. **TFLint** - Terraform-specific linting
   - Run locally before commits
   - Catches Terraform-specific issues

4. **Audit Tooling** - Custom security audits
   - Python-based audit scripts in `audit/`
   - Uses MCP servers for AWS best practices
   - Run periodically for compliance

## Workflows

- `super-linter.yml` - Automated linting on PRs
- `auto-approve.yml` - Dependabot auto-approval

## Dependabot

Configured in `dependabot.yml` for:

- GitHub Actions updates
- Python dependencies (audit scripts)

## Disabling Default CodeQL

If GitHub's default CodeQL scanning is enabled at the organization or repository level:

1. Go to repository **Settings** → **Code security and analysis**
2. Under **Code scanning**, disable **CodeQL analysis**
3. Or configure it to exclude this repository

This prevents the "no source code found" errors since CodeQL cannot analyze Terraform.
