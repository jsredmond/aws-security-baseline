# CloudTrail Module

## Purpose

This module deploys and configures AWS CloudTrail with comprehensive security features including:
- Multi-region trail for complete API activity logging
- KMS encryption for logs at rest
- CloudWatch Logs integration for real-time monitoring
- SNS notifications for CloudTrail events
- S3 bucket with versioning, lifecycle policies, and public access blocking
- Optional S3 data event logging

## Overview

AWS CloudTrail is a service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. This module creates a production-ready CloudTrail configuration that follows AWS security best practices.

## Usage

### Basic Example

```hcl
module "cloudtrail" {
  source = "./modules/cloudtrail"

  environment = "prod"
  
  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### Advanced Example

```hcl
module "cloudtrail" {
  source = "./modules/cloudtrail"

  environment                    = "prod"
  cloudwatch_logs_retention_days = 365
  s3_lifecycle_expiration_days   = 730
  kms_key_deletion_window        = 10
  enable_s3_data_events          = true
  
  common_tags = {
    Project     = "security-baseline"
    Owner       = "security-team"
    CostCenter  = "security"
    Compliance  = "required"
  }
}
```

## Input Variables

| Name | Description | Type | Default | Required | Validation |
|------|-------------|------|---------|----------|------------|
| environment | Environment name (dev, staging, prod) | string | - | yes | Must be dev, staging, or prod |
| cloudwatch_logs_retention_days | Number of days to retain CloudWatch logs | number | 365 | no | Must be valid CloudWatch retention value |
| s3_lifecycle_expiration_days | Number of days before S3 objects expire | number | 365 | no | Must be greater than 0 |
| kms_key_deletion_window | Number of days before KMS key deletion | number | 7 | no | Must be between 7 and 30 |
| enable_s3_data_events | Enable S3 data events in CloudTrail | bool | true | no | - |
| common_tags | Common tags to apply to all resources | map(string) | {} | no | - |

## Outputs

| Name | Description |
|------|-------------|
| trail_arn | ARN of the CloudTrail trail |
| trail_id | ID of the CloudTrail trail |
| s3_bucket_name | Name of the S3 bucket for CloudTrail logs |
| s3_bucket_arn | ARN of the S3 bucket for CloudTrail logs |
| kms_key_id | ID of the KMS key for CloudTrail encryption |
| kms_key_arn | ARN of the KMS key for CloudTrail encryption |
| cloudwatch_log_group_name | Name of the CloudWatch log group |
| cloudwatch_log_group_arn | ARN of the CloudWatch log group |
| sns_topic_arn | ARN of the SNS topic for CloudTrail alerts |

## Prerequisites

### AWS Permissions

The following AWS permissions are required to deploy this module:

**CloudTrail:**
- `cloudtrail:CreateTrail`
- `cloudtrail:UpdateTrail`
- `cloudtrail:StartLogging`
- `cloudtrail:PutEventSelectors`

**S3:**
- `s3:CreateBucket`
- `s3:PutBucketPolicy`
- `s3:PutBucketVersioning`
- `s3:PutEncryptionConfiguration`
- `s3:PutBucketPublicAccessBlock`
- `s3:PutLifecycleConfiguration`
- `s3:PutBucketNotification`
- `s3:PutBucketLogging`

**KMS:**
- `kms:CreateKey`
- `kms:CreateAlias`
- `kms:PutKeyPolicy`
- `kms:EnableKeyRotation`

**CloudWatch Logs:**
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutRetentionPolicy`

**IAM:**
- `iam:CreateRole`
- `iam:CreatePolicy`
- `iam:AttachRolePolicy`
- `iam:PassRole`

**SNS:**
- `sns:CreateTopic`
- `sns:SetTopicAttributes`

### Service Quotas

Ensure the following AWS service quotas are sufficient:
- CloudTrail trails per region: Default is 5
- S3 buckets per account: Default is 100
- KMS keys per region: Default is 1000

## Features

### Security

- **Encryption at Rest**: All logs are encrypted using KMS keys
- **Encryption in Transit**: CloudTrail uses HTTPS for all API calls
- **Log File Validation**: Enabled to detect tampering
- **Multi-Region Trail**: Captures events from all AWS regions
- **S3 Bucket Security**:
  - Versioning enabled
  - Public access blocked
  - Server-side encryption with KMS
  - Lifecycle policies for log retention

### Monitoring

- **CloudWatch Integration**: Real-time log delivery to CloudWatch Logs
- **SNS Notifications**: Alerts for CloudTrail events
- **EventBridge Integration**: S3 bucket notifications via EventBridge

### Compliance

- **Log Retention**: Configurable retention for both S3 and CloudWatch
- **Access Logging**: S3 access logs for audit trail
- **Key Rotation**: Automatic KMS key rotation enabled

## Notes

1. **Multi-Region Trail**: This module creates a multi-region trail, which means it will log events from all AWS regions. You only need to deploy this module in one region.

2. **S3 Data Events**: By default, S3 data events are enabled. This can generate a large volume of logs and increase costs. Set `enable_s3_data_events = false` if you don't need S3 object-level logging.

3. **Cost Considerations**:
   - CloudTrail management events are free for the first trail
   - S3 data events incur charges
   - CloudWatch Logs storage incurs charges
   - KMS key usage incurs charges

4. **Log Delivery Time**: CloudTrail typically delivers logs within 15 minutes of an API call.

5. **Dependencies**: The module uses explicit `depends_on` to ensure resources are created in the correct order, particularly for IAM roles and S3 bucket policies.

## Recent Security Enhancements

This module has been updated to implement AWS security best practices:

1. **Enhanced S3 Bucket Policy**: Added `aws:SourceArn` condition to prevent unauthorized CloudTrail logs from other accounts
2. **Enhanced SNS Topic Policy**: Added `aws:SourceArn` condition to prevent unauthorized SNS access
3. **Global Service Events**: Explicitly enabled `include_global_service_events` to ensure IAM and other global service events are captured
4. **CloudTrail Insights**: Enabled both `ApiCallRateInsight` and `ApiErrorRateInsight` for anomaly detection

These changes improve security posture by:
- Preventing confused deputy attacks on S3 and SNS resources
- Ensuring comprehensive logging of global AWS services
- Detecting unusual API activity patterns automatically

## Limitations

- The module does not support organization trails (trails that log events for all accounts in an AWS Organization)
- S3 bucket replication is not included in this module
- MFA delete for S3 bucket must be enabled manually via AWS CLI by root account user

## Version Requirements

- Terraform >= 1.0
- AWS Provider >= 5.0
- Random Provider >= 3.0
