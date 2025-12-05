# Deployment Testing Guide

This guide walks you through testing the AWS Security Baseline deployment.

## Prerequisites

1. **AWS Credentials**: Ensure you have AWS credentials configured
   ```bash
   aws configure
   # OR
   export AWS_ACCESS_KEY_ID="your-key"
   export AWS_SECRET_ACCESS_KEY="your-secret"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

2. **Terraform**: Version 1.14.1 or later installed

3. **AWS Permissions**: Your IAM user/role needs permissions for:
   - CloudTrail: Create trails, S3 buckets, KMS keys, CloudWatch logs, SNS topics
   - AWS Config: Create recorders, delivery channels, S3 buckets, IAM roles
   - GuardDuty: Create detectors
   - Detective: Create graphs (requires 48 hours of GuardDuty data)
   - Security Hub: Enable Security Hub, subscribe to standards
   - S3: Create and configure buckets
   - KMS: Create and manage keys
   - IAM: Create roles and policies

## Step 1: Review Configuration

The `terraform.tfvars` file has been created with sensible defaults:

```hcl
environment = "dev"
aws_region  = "us-east-1"

# Modules enabled
enable_cloudtrail   = true
enable_config       = true
enable_guardduty    = true
enable_detective    = false  # Requires 48 hours of GuardDuty data
enable_securityhub  = true
```

**Customize as needed** by editing `terraform.tfvars`.

## Step 2: Initialize Terraform

```bash
terraform init
```

This will:
- Initialize the local backend (state stored in `terraform.tfstate`)
- Download required providers (AWS, Random)
- Initialize all modules

## Step 3: Validate Configuration

```bash
terraform validate
```

Should return: "Success! The configuration is valid."

## Step 4: Preview Changes

```bash
terraform plan -out=tfplan
```

This will show you:
- **42 resources** to be created (with Detective disabled)
- All CloudTrail, Config, GuardDuty, and Security Hub resources
- S3 buckets, KMS keys, IAM roles, etc.

**Review the plan carefully** to ensure:
- Resource names match your expectations
- Tags are correct
- No unexpected resources

## Step 5: Apply Changes (Deploy)

**⚠️ WARNING: This will create real AWS resources that may incur costs!**

```bash
terraform apply tfplan
```

Or interactively:

```bash
terraform apply
```

Type `yes` when prompted to confirm.

**Expected Duration**: 5-10 minutes

## Step 6: Verify Deployment

### Check Terraform Outputs

```bash
terraform output
```

You should see outputs for:
- CloudTrail trail ARN, bucket name, KMS key ID
- Config recorder name, bucket name, delivery channel ID
- GuardDuty detector ID
- Security Hub account ARN and enabled standards

### Verify in AWS Console

1. **CloudTrail**:
   - Go to CloudTrail console
   - Verify trail `dev-cloudtrail` is active
   - Check that logging is enabled

2. **AWS Config**:
   - Go to Config console
   - Verify recorder `dev-config-recorder` is recording
   - Check delivery channel is active

3. **GuardDuty**:
   - Go to GuardDuty console
   - Verify detector is enabled
   - Check findings (may be empty initially)

4. **Security Hub**:
   - Go to Security Hub console
   - Verify Security Hub is enabled
   - Check that CIS and AWS Foundational standards are enabled

5. **S3 Buckets**:
   - Go to S3 console
   - Verify CloudTrail and Config buckets exist
   - Check encryption and versioning are enabled

6. **KMS Keys**:
   - Go to KMS console
   - Verify keys for CloudTrail, Config, and CloudWatch exist
   - Check key rotation is enabled

## Step 7: Test Functionality

### CloudTrail Test

```bash
# Make an AWS API call
aws s3 ls

# Wait 5-10 minutes, then check CloudTrail logs
aws cloudtrail lookup-events --max-results 10
```

### Config Test

```bash
# Check Config is recording
aws configservice describe-configuration-recorder-status

# View configuration items
aws configservice list-discovered-resources --resource-type AWS::EC2::Instance
```

### GuardDuty Test

```bash
# Check detector status
aws guardduty list-detectors

# View findings (may be empty initially)
DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)
aws guardduty list-findings --detector-id $DETECTOR_ID
```

### Security Hub Test

```bash
# Check Security Hub status
aws securityhub describe-hub

# View enabled standards
aws securityhub get-enabled-standards
```

## Step 8: Monitor Costs

Check AWS Cost Explorer or Billing Dashboard for:
- S3 storage costs (minimal initially)
- CloudTrail event logging costs
- Config recording costs
- GuardDuty analysis costs
- Security Hub costs

**Estimated Monthly Cost** (us-east-1, light usage):
- CloudTrail: $2-5
- AWS Config: $2-10
- GuardDuty: $4-10
- Security Hub: $0 (first 30 days free, then ~$1.20/month)
- S3 Storage: $0.50-2
- **Total: ~$10-30/month**

## Step 9: Clean Up (Optional)

To destroy all resources:

```bash
terraform destroy
```

Type `yes` when prompted.

**⚠️ WARNING**: This will delete:
- All S3 buckets (if empty)
- All KMS keys (scheduled for deletion)
- All CloudTrail trails
- All Config recorders
- GuardDuty detector
- Security Hub configuration

**Note**: S3 buckets with `force_destroy = false` must be emptied manually before destruction.

## Troubleshooting

### Issue: "Access Denied" errors

**Solution**: Check IAM permissions. Your user/role needs permissions for all services being deployed.

### Issue: "Bucket already exists"

**Solution**: S3 bucket names are globally unique. The random suffix should prevent this, but if it occurs, run:

```bash
terraform destroy
terraform apply
```

### Issue: "Detective requires 48 hours of GuardDuty data"

**Solution**: This is expected. Set `enable_detective = false` initially, then enable after 48 hours.

### Issue: "KMS key deletion pending"

**Solution**: KMS keys have a deletion window (7-10 days). Wait for the deletion window to expire, or use the AWS console to cancel deletion.

### Issue: Plan shows unexpected changes

**Solution**: Run `terraform refresh` to sync state with actual AWS resources.

## Next Steps

After successful deployment:

1. **Configure Notifications**: Set up SNS subscriptions for CloudTrail alerts
2. **Enable Detective**: After 48 hours of GuardDuty data
3. **Configure Config Rules**: Add compliance rules in AWS Config
4. **Review Security Hub Findings**: Address any security issues
5. **Set Up Monitoring**: Create CloudWatch dashboards
6. **Document**: Update your team's documentation with deployment details

## Remote State (Optional)

To migrate to S3 remote state:

1. Create S3 bucket and DynamoDB table
2. Uncomment the backend configuration in `backend.tf`
3. Run `terraform init -migrate-state`

See `backend.tf` for detailed instructions.

## Support

- Review module READMEs in `modules/` directory
- Check `MIGRATION.md` for migration guidance
- Consult AWS documentation for service-specific issues

