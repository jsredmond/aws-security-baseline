# Deploying an AWS Security Baseline with Terraform

[![GitHub Super-Linter](https://github.com/jsredmond/aws-security-baseline/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)

## Features

This repository provides Terraform template files to setup and enable a baseline of AWS security tools as a good foundation. The following services are setup and configured:

* [AWS CloudTrail](https://aws.amazon.com/cloudtrail/)
* [AWS Config](https://aws.amazon.com/config/)
* [Amazon Detective](https://aws.amazon.com/detective/)
* [Amazon GuardDuty](https://aws.amazon.com/guardduty/)
* [AWS Security Hub](https://aws.amazon.com/security-hub/)

## Terraform versions

For Terraform 0.13 or later use any version from `v4.48.0` of hashicorp/aws module or newer.

## Authors

Repository managed by [Jeremy Redmond](https://github.com/jsredmond).

## License

MIT Licensed. See LICENSE for full details.