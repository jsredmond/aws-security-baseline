# Backend Configuration for Remote State Management
# This configuration uses S3 for state storage with encryption enabled
# and DynamoDB for state locking to prevent concurrent modifications.
#
# Requirements: 5.1, 5.2, 5.3, 5.5

terraform {
  backend "s3" {
    # S3 bucket for state storage
    # Use partial configuration or -backend-config flag to set these values
    # bucket = var.terraform_state_bucket  # Not allowed in backend block
    # key    = var.terraform_state_key     # Not allowed in backend block
    # region = var.aws_region              # Not allowed in backend block

    # Enable encryption at rest
    encrypt = true

    # DynamoDB table for state locking
    # dynamodb_table = var.terraform_state_lock_table  # Not allowed in backend block

    # Additional security settings
    # Enable versioning on the S3 bucket (configured separately)
    # Enable server-side encryption with KMS (configured separately)
  }
}

# Note: Backend configuration does not support variable interpolation.
# You must provide these values using one of the following methods:
#
# 1. Partial Configuration File (recommended):
#    Create a file named backend-config.hcl with:
#      bucket         = "your-terraform-state-bucket"
#      key            = "security-baseline/terraform.tfstate"
#      region         = "us-east-1"
#      dynamodb_table = "your-terraform-state-lock-table"
#    
#    Then run: terraform init -backend-config=backend-config.hcl
#
# 2. Command Line Flags:
#    terraform init \
#      -backend-config="bucket=your-terraform-state-bucket" \
#      -backend-config="key=security-baseline/terraform.tfstate" \
#      -backend-config="region=us-east-1" \
#      -backend-config="dynamodb_table=your-terraform-state-lock-table"
#
# 3. Environment Variables:
#    export TF_CLI_ARGS_init="-backend-config=bucket=your-terraform-state-bucket"
#
# Prerequisites:
# - S3 bucket must exist with versioning enabled
# - S3 bucket must have encryption enabled (preferably with KMS)
# - DynamoDB table must exist with LockID as the primary key (String type)
# - IAM permissions must allow s3:GetObject, s3:PutObject, dynamodb:GetItem, dynamodb:PutItem
