# Deploying an AWS Security Baseline with Terraform

[![Super-Linter](https://github.com/jsredmond/aws-security-baseline/actions/workflows/linter.yml/badge.svg)](https://github.com/jsredmond/aws-security-baseline/actions/workflows/linter.yml)

## Features

This repository provides Terraform template files to setup and enable a baseline of AWS security tools as a good foundation. The following services are setup and configured:

* [AWS CloudTrail](https://aws.amazon.com/cloudtrail/)
* [AWS Config](https://aws.amazon.com/config/)
* [Amazon Detective](https://aws.amazon.com/detective/)
* [Amazon GuardDuty](https://aws.amazon.com/guardduty/)
* [AWS Security Hub](https://aws.amazon.com/security-hub/)

## Terraform versions

For Terraform 1.14.4 or later use any version from `v5.95.0` of hashicorp/aws module or newer.

## Authors

Repository managed by [Jeremy Redmond](https://github.com/jsredmond).

## License

MIT Licensed. See LICENSE for full details.