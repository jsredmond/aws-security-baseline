"""
Validation functions for the AWS Security Baseline Deployment Wizard.

This module provides validation functions for user inputs including
AWS regions, environment names, and tag keys.

**Validates: Requirements 3.2, 3.3, 4.2, 5.2**
"""

import re


# AWS region pattern: 2 lowercase letters, hyphen, region name, hyphen, number
# Examples: us-east-1, eu-west-2, ap-southeast-1
AWS_REGION_PATTERN = re.compile(r"^[a-z]{2}-[a-z]+-\d+$")

# Environment pattern: alphanumeric characters and hyphens only
# Examples: dev, staging, prod, my-env-1
ENVIRONMENT_PATTERN = re.compile(r"^[a-zA-Z0-9-]+$")


def validate_region(region: str) -> bool:
    """Validate that a string is a valid AWS region format.

    AWS regions follow the pattern: <area>-<location>-<number>
    Examples: us-east-1, eu-west-2, ap-southeast-1

    Args:
        region: The region string to validate

    Returns:
        True if the region matches the AWS region pattern, False otherwise

    **Validates: Requirements 3.2, 3.3**
    """
    if not region or not isinstance(region, str):
        return False
    return bool(AWS_REGION_PATTERN.match(region))


def validate_environment(env: str) -> bool:
    """Validate that an environment name contains only valid characters.

    Valid environment names contain only alphanumeric characters and hyphens.
    Examples: dev, staging, prod, my-env-1

    Args:
        env: The environment name to validate

    Returns:
        True if the environment name is valid, False otherwise

    **Validates: Requirements 4.2**
    """
    if not env or not isinstance(env, str):
        return False
    return bool(ENVIRONMENT_PATTERN.match(env))


def validate_tag_key(key: str) -> bool:
    """Validate that a tag key is not empty.

    Tag keys must be non-empty strings.

    Args:
        key: The tag key to validate

    Returns:
        True if the tag key is non-empty, False otherwise

    **Validates: Requirements 5.2**
    """
    if not isinstance(key, str):
        return False
    return len(key.strip()) > 0
