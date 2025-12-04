# AWS Config Module

## Purpose

This module deploys and configures AWS Config with comprehensive security features including:
- Configuration recording for all supported AWS resources
- KMS encryption for configuration snapshots
- S3 bucket with versioning, lifecycle policies, and public access blocking
- Automatic delivery of configuration snapshots and history
- Optional global resource recording (IAM, CloudFront, etc.)

## Overview

AWS Config is a service that enables you to assess, audit, and evaluate the configurations of your AWS resources. This module creates a production-ready AWS Config setup that follows AWS security best practices and enables continuous monitoring of resource configurations.

## Usage

### Basic Example

```hcl
module "config" {
  source = "./modules/config"

  environment = "prod"
  
  common_tags = {
    Project = "security-baseline"
    Owner   = "security-team"
  }
}
```

### Advanced Example

```hcl
module "config" {
  source = "./modules/config"

  environment                  = "prod"
  s3_lifecycle_expiration_days = 730
  kms_key_deletion_window      = 10
  include_global_resources     = true
  
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
| s3_lifecycle_expiration_days | Number of days before S3 objects expire | number | 365 | no | Must be greater than 0 |
| kms_key_deletion_window | Number of days before KMS key deletion | number | 10 | no | Must be between 7 and 30 |
| include_global_resources | Include global resources in Config recording | bool | true | no | - |
| common_tags | Common tags to apply to all resources | map(string) | {} | no | - |

## Outputs

| Name | Description |
|------|-------------|
| recorder_name | Name of the AWS Config configuration recorder |
| recorder_id | ID of the AWS Config configuration recorder |
| s3_bucket_name | Name of the S3 bucket for Config snapshots |
| s3_bucket_arn | ARN of the S3 bucket for Config snapshots |
| delivery_channel_id | ID of the AWS Config delivery channel |
| kms_key_id | ID of the KMS key for Config encryption |
| kms_key_arn | ARN of the KMS key for Config encryption |
| iam_role_arn | ARN of the IAM role for AWS Config |

## Prerequisites

### AWS Permissions

The following AWS permissions are required to deploy this module:

**AWS Config:**
- `config:PutConfigurationRecorder`
- `config:PutDeliveryChannel`
- `config:StartConfigurationRecorder`
- `config:DescribeConfigurationRecorders`
- `config:DescribeDeliveryChannels`

**S3:**
- `s3:CreateBucket`
- `s3:PutBucketPolicy`
- `s3:PutBucketVersioning`
- `s3:PutEncryptionConfiguration`
- `s3:PutBucketPublicAccessBlock`
- `s3:PutLifecycleConfiguration`
- `s3:PutBucketNotification`
- `s3:PutBucketLogging`
- `s3:PutReplicationConfiguration`

**KMS:**
- `kms:CreateKey`
- `kms:CreateAlias`
- `kms:PutKeyPolicy`
- `kms:EnableKeyRotation`

**IAM:**
- `iam:CreateRole`
- `iam:CreatePolicy`
- `iam:AttachRolePolicy`
- `iam:PutRolePolicy`
- `iam:PassRole`

### Service Quotas

Ensure the following AWS service quotas are sufficient:
- Config recorders per region: Default is 1
- S3 buckets per account: Default is 100
- KMS keys per region: Default is 1000

## Features

### Security

- **Encryption at Rest**: All configuration snapshots are encrypted using KMS keys
- **Encryption in Transit**: AWS Config uses HTTPS for all API calls
- **S3 Bucket Security**: 
  - Versioning enabled
  - Public access blocked
  - Server-side encryption with KMS
  - Lifecycle policies for snapshot retention
  - Access logging enabled
  - EventBridge notifications enabled

### Monitoring

- **Continuous Recording**: Monitors configuration changes for all supported resources
- **Configuration History**: Maintains historical record of resource configurations
- **Delivery Channel**: Automatic delivery of configuration snapshots to S3
- **EventBridge Integration**: S3 bucket notifications via EventBridge

### Compliance

- **Global Resources**: Optional recording of global resources (IAM, CloudFront, Route 53)
- **All Resources**: Records all supported AWS resource types
- **Snapshot Retention**: Configurable retention for configuration snapshots
- **Key Rotation**: Automatic KMS key rotation enabled

## Notes

1. **Global Resources**: By default, this module includes global resources (IAM, CloudFront, etc.) in the recording. Set `include_global_resources = false` if you're deploying Config in multiple regions to avoid duplicate recording of global resources. Only enable this in one region per account.

2. **Configuration Recorder**: AWS Config allows only one configuration recorder per region. If you already have a recorder in the region, this module will fail. You'll need to import the existing recorder or delete it first.

3. **Cost Considerations**: 
   - AWS Config charges per configuration item recorded
   - S3 storage charges for configuration snapshots
   - KMS key usage charges
   - Consider lifecycle policies to manage costs

4. **Recording Delay**: AWS Config typically records configuration changes within a few minutes of the change occurring.

5. **Dependencies**: The module uses explicit `depends_on` to ensure resources are created in the correct order, particularly for the configuration recorder and delivery channel.

6. **S3 Replication**: The module includes S3 replication configuration. You'll need to update the replication role ARN and target bucket ARN to match your environment, or remove this resource if replication is not needed.

## Limitations

- Only one configuration recorder is allowed per region
- The module does not create AWS Config Rules (compliance rules)
- Organization-level Config aggregation is not included
- S3 replication requires manual configuration of the target bucket and IAM role

## Version Requirements

- Terraform >= 1.0
- AWS Provider >= 5.0
- Random Provider >= 3.0

## Example: Multi-Region Deployment

When deploying AWS Config across multiple regions, ensure only one region records global resources:

```hcl
# Primary region (us-east-1) - records global resources
module "config_primary" {
  source = "./modules/config"

  environment              = "prod"
  include_global_resources = true
  
  providers = {
    aws = aws.us-east-1
  }
}

# Secondary region (us-west-2) - does not record global resources
module "config_secondary" {
  source = "./modules/config"

  environment              = "prod"
  include_global_resources = false
  
  providers = {
    aws = aws.us-west-2
  }
}
```
