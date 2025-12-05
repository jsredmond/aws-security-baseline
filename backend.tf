# Backend Configuration for State Management
#
# By default, this uses local state storage (terraform.tfstate file).
# For production use, consider migrating to remote state with S3 backend.
#
# Requirements: 5.1, 5.2, 5.3, 5.5

# Default: Local backend (no configuration needed)
# State will be stored in terraform.tfstate in the current directory

# To use S3 remote backend instead, uncomment and configure the following:
#
# terraform {
#   backend "s3" {
#     # S3 bucket for state storage
#     # Use partial configuration or -backend-config flag to set these values
#     # bucket = "your-terraform-state-bucket"
#     # key    = "security-baseline/terraform.tfstate"
#     # region = "us-east-1"
#
#     # Enable encryption at rest
#     encrypt = true
#
#     # DynamoDB table for state locking
#     # dynamodb_table = "your-terraform-state-lock-table"
#   }
# }
#
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
# Prerequisites for S3 backend:
# - S3 bucket must exist with versioning enabled
# - S3 bucket must have encryption enabled (preferably with KMS)
# - DynamoDB table must exist with LockID as the primary key (String type)
# - IAM permissions must allow s3:GetObject, s3:PutObject, dynamodb:GetItem, dynamodb:PutItem
