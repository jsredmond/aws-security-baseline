# Migration Guide: Monolithic to Modular Structure

This guide provides step-by-step instructions for migrating from the monolithic Terraform structure to the new modular architecture.

## Overview

The migration transforms the flat structure where all resources are defined in the root module into a modular structure with dedicated modules for each AWS security service. This improves maintainability, testability, and reusability.

### What's Changing

**Before (Monolithic):**
```
.
├── cloudtrail.tf       # All CloudTrail resources
├── config.tf           # All Config resources
├── detective.tf        # Detective resources
├── guardduty.tf        # GuardDuty resources
├── securityhub.tf      # Security Hub resources
├── random.tf           # Shared random ID
├── providers.tf
├── variables.tf
└── outputs.tf
```

**After (Modular):**
```
.
├── main.tf                    # Module calls
├── backend.tf                 # Remote state configuration
├── providers.tf
├── variables.tf               # Root-level variables
├── outputs.tf                 # Aggregated outputs
└── modules/
    ├── cloudtrail/
    ├── config/
    ├── detective/
    ├── guardduty/
    └── securityhub/
```

## Prerequisites

Before starting the migration:

1. **Backup your current state file:**
   ```bash
   terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate
   ```

2. **Ensure you're on the correct branch:**
   ```bash
   git checkout feature/terraform-modularization
   ```

3. **Verify all modules are created:**
   ```bash
   ls -la modules/
   # Should show: cloudtrail, config, detective, guardduty, securityhub
   ```

4. **Initialize all modules:**
   ```bash
   terraform init
   ```

## Migration Process

### Phase 1: Preparation (5 minutes)

1. **Create a backup of your current state:**
   ```bash
   terraform state pull > backup-pre-migration-$(date +%Y%m%d-%H%M%S).tfstate
   ```

2. **Verify current state:**
   ```bash
   terraform state list
   ```
   
   Save this output for reference during migration.

3. **Run a plan to ensure no pending changes:**
   ```bash
   terraform plan
   ```
   
   If there are pending changes, apply them first or note them for later.

### Phase 2: State Migration (30-45 minutes)

**IMPORTANT:** The order of operations matters. Follow these steps exactly.

#### Step 1: Migrate CloudTrail Resources

```bash
# Random ID
terraform state mv random_id.cloudtrail_suffix module.cloudtrail[0].random_id.suffix

# KMS Keys
terraform state mv aws_kms_key.cloudtrail module.cloudtrail[0].aws_kms_key.cloudtrail
terraform state mv aws_kms_alias.cloudtrail module.cloudtrail[0].aws_kms_alias.cloudtrail
terraform state mv aws_kms_key.cloudtrail_cloudwatch module.cloudtrail[0].aws_kms_key.cloudwatch
terraform state mv aws_kms_alias.cloudtrail_cloudwatch module.cloudtrail[0].aws_kms_alias.cloudwatch

# S3 Bucket and configurations
terraform state mv aws_s3_bucket.cloudtrail_bucket module.cloudtrail[0].aws_s3_bucket.cloudtrail
terraform state mv aws_s3_bucket_versioning.cloudtrail_versioning module.cloudtrail[0].aws_s3_bucket_versioning.main
terraform state mv aws_s3_bucket_server_side_encryption_configuration.cloudtrail_encryption module.cloudtrail[0].aws_s3_bucket_server_side_encryption_configuration.main
terraform state mv aws_s3_bucket_public_access_block.cloudtrail_public_access_block module.cloudtrail[0].aws_s3_bucket_public_access_block.main
terraform state mv aws_s3_bucket_lifecycle_configuration.cloudtrail_lifecycle module.cloudtrail[0].aws_s3_bucket_lifecycle_configuration.main
terraform state mv aws_s3_bucket_policy.cloudtrail_bucket_policy module.cloudtrail[0].aws_s3_bucket_policy.main

# CloudWatch resources
terraform state mv aws_cloudwatch_log_group.cloudtrail_log_group module.cloudtrail[0].aws_cloudwatch_log_group.main
terraform state mv aws_cloudwatch_log_stream.cloudtrail_log_stream module.cloudtrail[0].aws_cloudwatch_log_stream.main

# IAM resources
terraform state mv aws_iam_role.cloudtrail_cloudwatch_role module.cloudtrail[0].aws_iam_role.cloudwatch
terraform state mv aws_iam_role_policy.cloudtrail_cloudwatch_policy module.cloudtrail[0].aws_iam_role_policy.cloudwatch

# SNS resources
terraform state mv aws_sns_topic.cloudtrail_alerts module.cloudtrail[0].aws_sns_topic.alerts
terraform state mv aws_sns_topic_policy.cloudtrail_alerts_policy module.cloudtrail[0].aws_sns_topic_policy.alerts

# CloudTrail trail
terraform state mv aws_cloudtrail.main_trail module.cloudtrail[0].aws_cloudtrail.main
```

**Verify CloudTrail migration:**
```bash
terraform state list | grep cloudtrail
# All resources should now be under module.cloudtrail[0]
```

#### Step 2: Migrate Config Resources

```bash
# Random ID
terraform state mv random_id.config_suffix module.config[0].random_id.suffix

# KMS Key
terraform state mv aws_kms_key.config module.config[0].aws_kms_key.config
terraform state mv aws_kms_alias.config module.config[0].aws_kms_alias.config

# S3 Bucket and configurations
terraform state mv aws_s3_bucket.config_bucket module.config[0].aws_s3_bucket.config
terraform state mv aws_s3_bucket_versioning.config_versioning module.config[0].aws_s3_bucket_versioning.main
terraform state mv aws_s3_bucket_server_side_encryption_configuration.config_encryption module.config[0].aws_s3_bucket_server_side_encryption_configuration.main
terraform state mv aws_s3_bucket_public_access_block.config_public_access_block module.config[0].aws_s3_bucket_public_access_block.main
terraform state mv aws_s3_bucket_lifecycle_configuration.config_lifecycle module.config[0].aws_s3_bucket_lifecycle_configuration.main
terraform state mv aws_s3_bucket_policy.config_bucket_policy module.config[0].aws_s3_bucket_policy.main

# IAM resources
terraform state mv aws_iam_role.config_role module.config[0].aws_iam_role.main
terraform state mv aws_iam_role_policy_attachment.config_policy module.config[0].aws_iam_role_policy_attachment.main

# Config resources
terraform state mv aws_config_configuration_recorder.main module.config[0].aws_config_configuration_recorder.main
terraform state mv aws_config_delivery_channel.main module.config[0].aws_config_delivery_channel.main
terraform state mv aws_config_configuration_recorder_status.main module.config[0].aws_config_configuration_recorder_status.main
```

**Verify Config migration:**
```bash
terraform state list | grep config
# All resources should now be under module.config[0]
```

#### Step 3: Migrate GuardDuty Resources

```bash
# GuardDuty detector
terraform state mv aws_guardduty_detector.main module.guardduty[0].aws_guardduty_detector.main

# Organization configuration (if exists)
terraform state mv aws_guardduty_organization_configuration.main module.guardduty[0].aws_guardduty_organization_configuration.main 2>/dev/null || echo "No organization config to migrate"
```

**Verify GuardDuty migration:**
```bash
terraform state list | grep guardduty
# All resources should now be under module.guardduty[0]
```

#### Step 4: Migrate Detective Resources

```bash
# Detective graph
terraform state mv aws_detective_graph.main module.detective[0].aws_detective_graph.main
```

**Verify Detective migration:**
```bash
terraform state list | grep detective
# All resources should now be under module.detective[0]
```

#### Step 5: Migrate Security Hub Resources

```bash
# Security Hub account
terraform state mv aws_securityhub_account.main module.securityhub[0].aws_securityhub_account.main

# Standards subscriptions (if they exist)
terraform state mv aws_securityhub_standards_subscription.cis module.securityhub[0].aws_securityhub_standards_subscription.cis 2>/dev/null || echo "No CIS standard to migrate"
terraform state mv aws_securityhub_standards_subscription.aws_foundational module.securityhub[0].aws_securityhub_standards_subscription.aws_foundational 2>/dev/null || echo "No AWS Foundational standard to migrate"
terraform state mv aws_securityhub_standards_subscription.pci_dss module.securityhub[0].aws_securityhub_standards_subscription.pci_dss 2>/dev/null || echo "No PCI DSS standard to migrate"
```

**Verify Security Hub migration:**
```bash
terraform state list | grep securityhub
# All resources should now be under module.securityhub[0]
```

#### Step 6: Remove Old Shared Random ID

```bash
# Remove the old shared random_id if it exists
terraform state rm random_id.suffix 2>/dev/null || echo "No shared random_id to remove"
```

### Phase 3: Validation (10-15 minutes)

1. **Verify all resources are migrated:**
   ```bash
   terraform state list
   ```
   
   All resources should now be under `module.<service>[0]` paths.

2. **Run terraform plan:**
   ```bash
   terraform plan
   ```
   
   **Expected result:** No resources should be marked for destruction. You may see:
   - Minor changes to tags (adding Module tag)
   - Updates to resource names or descriptions
   - Changes to computed attributes
   
   **Unexpected results that require investigation:**
   - Any resources marked for destruction (red `-`)
   - Any resources marked for creation (green `+`)
   - Any resources marked for replacement (red/green `+/-`)

3. **Verify module outputs:**
   ```bash
   terraform output
   ```
   
   All outputs should still be available and show correct values.

4. **Run validation:**
   ```bash
   terraform validate
   ```

5. **Run security scans:**
   ```bash
   checkov -d . --framework terraform
   tflint --recursive
   ```

### Phase 4: Apply Changes (5-10 minutes)

If the plan looks correct:

1. **Apply the changes:**
   ```bash
   terraform apply
   ```
   
   Review the plan one more time before confirming.

2. **Verify resources in AWS Console:**
   - Check that all services are still enabled
   - Verify CloudTrail is still logging
   - Verify Config is still recording
   - Check GuardDuty findings
   - Review Security Hub dashboard

## Rollback Procedures

If something goes wrong during migration, you can rollback:

### Option 1: Restore from State Backup

```bash
# 1. Stop any running terraform operations
# Press Ctrl+C if terraform is running

# 2. Restore the backup state
terraform state push backup-pre-migration-YYYYMMDD-HHMMSS.tfstate

# 3. Verify restoration
terraform state list

# 4. Run a plan to verify
terraform plan
```

### Option 2: Manual State Reversal

If you need to reverse specific state moves:

```bash
# Reverse the state mv commands in opposite order
# Example for CloudTrail:
terraform state mv module.cloudtrail[0].aws_cloudtrail.main aws_cloudtrail.main_trail
terraform state mv module.cloudtrail[0].aws_sns_topic_policy.alerts aws_sns_topic_policy.cloudtrail_alerts_policy
# ... continue for all resources
```

### Option 3: Revert Code Changes

```bash
# 1. Checkout the previous branch
git checkout main

# 2. Restore state from backup
terraform state push backup-pre-migration-YYYYMMDD-HHMMSS.tfstate

# 3. Verify
terraform plan
```

## Troubleshooting

### Issue: "Resource not found in state"

**Symptom:** Error message like `Error: Invalid target address: Resource X does not exist in the state`

**Solution:**
1. Check the exact resource name in state: `terraform state list | grep <resource>`
2. Verify the resource name matches exactly (case-sensitive)
3. If the resource doesn't exist, it may have already been migrated or never existed

### Issue: "Module not found"

**Symptom:** Error message like `Error: Module not installed`

**Solution:**
```bash
terraform init
```

### Issue: Plan shows resources being destroyed

**Symptom:** `terraform plan` shows resources with `-` (destruction)

**Solution:**
1. **DO NOT APPLY** - this indicates a problem
2. Check that all state moves were completed correctly
3. Verify module source paths in main.tf
4. Ensure all required variables are passed to modules
5. Compare resource configurations between old and new structure

### Issue: "Error acquiring state lock"

**Symptom:** Cannot run terraform commands due to state lock

**Solution:**
```bash
# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

### Issue: Outputs are empty or incorrect

**Symptom:** `terraform output` shows empty values

**Solution:**
1. Check that modules are exporting outputs correctly
2. Verify root outputs.tf references module outputs correctly
3. Run `terraform refresh` to update output values

### Issue: Module count/for_each mismatch

**Symptom:** Error about count or for_each changing

**Solution:**
1. Ensure enable flags match your previous configuration
2. If a service was enabled before, set `enable_<service> = true`
3. Check that conditional logic in main.tf matches your setup

## Post-Migration Checklist

After successful migration:

- [ ] All `terraform state list` resources are under module paths
- [ ] `terraform plan` shows no unexpected changes
- [ ] `terraform apply` completed successfully
- [ ] All outputs are correct: `terraform output`
- [ ] Security scans pass: `checkov -d .`
- [ ] Validation passes: `terraform validate`
- [ ] All AWS services are functioning in console
- [ ] CloudTrail is logging events
- [ ] Config is recording changes
- [ ] GuardDuty is detecting threats
- [ ] Security Hub is aggregating findings
- [ ] State backup is stored securely
- [ ] Documentation is updated
- [ ] Team is notified of changes

## Best Practices

1. **Always backup state before migration**
2. **Test in a non-production environment first**
3. **Migrate during a maintenance window**
4. **Have a rollback plan ready**
5. **Verify each phase before proceeding**
6. **Keep state backups for at least 30 days**
7. **Document any deviations from this guide**
8. **Run security scans after migration**

## Additional Resources

- [Terraform State Management](https://www.terraform.io/docs/language/state/index.html)
- [Terraform State Commands](https://www.terraform.io/docs/cli/commands/state/index.html)
- [Module Documentation](./modules/)
- [Backend Configuration](./README.md#backend-configuration)

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review module READMEs in `modules/` directory
3. Consult Terraform documentation
4. Open an issue in the repository

## Migration Timeline

Estimated time for complete migration:

- **Preparation:** 5 minutes
- **State Migration:** 30-45 minutes
- **Validation:** 10-15 minutes
- **Apply Changes:** 5-10 minutes
- **Total:** 50-75 minutes

Plan for additional time if issues arise or if this is your first migration.
