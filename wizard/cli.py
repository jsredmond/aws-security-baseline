"""
CLI argument parser for the AWS Security Baseline Deployment Wizard.

This module provides command-line argument parsing for non-interactive mode,
allowing users to automate deployments with pre-specified options.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
"""

import argparse
from typing import List, Optional, Tuple

from wizard.models import AVAILABLE_MODULES, WizardConfig
from wizard.validators import validate_region, validate_environment


def parse_tag(tag_string: str) -> Tuple[str, str]:
    """Parse a tag string in KEY=VALUE format.

    Args:
        tag_string: Tag string in KEY=VALUE format

    Returns:
        Tuple of (key, value)

    Raises:
        argparse.ArgumentTypeError: If tag format is invalid
    """
    if "=" not in tag_string:
        raise argparse.ArgumentTypeError(
            f"Invalid tag format: '{tag_string}'. Expected KEY=VALUE format."
        )

    key, _, value = tag_string.partition("=")

    if not key:
        raise argparse.ArgumentTypeError(
            f"Invalid tag format: '{tag_string}'. Tag key cannot be empty."
        )

    return (key, value)


def validate_region_arg(region: str) -> str:
    """Validate region argument.

    Args:
        region: Region string to validate

    Returns:
        The validated region string

    Raises:
        argparse.ArgumentTypeError: If region format is invalid
    """
    if not validate_region(region):
        raise argparse.ArgumentTypeError(
            f"Invalid region format: '{region}'. Expected format: us-east-1"
        )
    return region


def validate_environment_arg(env: str) -> str:
    """Validate environment argument.

    Args:
        env: Environment string to validate

    Returns:
        The validated environment string

    Raises:
        argparse.ArgumentTypeError: If environment format is invalid
    """
    if not validate_environment(env):
        raise argparse.ArgumentTypeError(
            f"Invalid environment name: '{env}'. Use only letters, numbers, and hyphens."
        )
    return env


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="wizard",
        description="AWS Security Baseline Deployment Wizard - Configure and deploy AWS security services",
        epilog="For interactive mode, run without arguments. For more information, visit: https://github.com/jsredmond/aws-security-baseline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Module selection
    parser.add_argument(
        "--all-modules",
        action="store_true",
        help="Enable all security modules (CloudTrail, Config, GuardDuty, Detective, Security Hub, IAM Access Analyzer, Inspector, Macie)",
    )

    # Region configuration
    parser.add_argument(
        "--region",
        type=validate_region_arg,
        metavar="REGION",
        help="AWS region for deployment (e.g., us-east-1, eu-west-1). Default: us-east-1",
    )

    # Environment configuration
    parser.add_argument(
        "--env",
        type=validate_environment_arg,
        metavar="ENV",
        help="Environment name (e.g., dev, staging, prod). Only alphanumeric characters and hyphens allowed.",
    )

    # Tag configuration
    parser.add_argument(
        "--tag",
        type=parse_tag,
        action="append",
        metavar="KEY=VALUE",
        dest="tags",
        help="Add a resource tag in KEY=VALUE format. Can be specified multiple times.",
    )

    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional list of arguments to parse. If None, uses sys.argv.

    Returns:
        Parsed arguments namespace

    **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
    """
    parser = create_parser()
    return parser.parse_args(args)


def has_cli_args(args: argparse.Namespace) -> bool:
    """Check if any CLI arguments were provided (non-interactive mode).

    Args:
        args: Parsed arguments namespace

    Returns:
        True if any arguments were provided, False for interactive mode
    """
    return (
        args.all_modules
        or args.region is not None
        or args.env is not None
        or args.tags is not None
    )


def build_config_from_args(args: argparse.Namespace) -> WizardConfig:
    """Build a WizardConfig from parsed CLI arguments.

    Args:
        args: Parsed arguments namespace

    Returns:
        WizardConfig populated from CLI arguments

    **Validates: Requirements 9.1, 9.3, 9.4**
    """
    config = WizardConfig()

    # Handle module selection
    if args.all_modules:
        for module in AVAILABLE_MODULES:
            config.modules[module.name] = True

    # Handle region
    if args.region:
        config.region = args.region

    # Handle environment
    if args.env:
        config.environment = args.env

    # Handle tags - start with auto-included tags
    config.tags = {
        "Environment": config.environment,
        "ManagedBy": "Terraform",
    }

    # Add user-specified tags
    if args.tags:
        for key, value in args.tags:
            config.tags[key] = value

    return config


def get_help_text() -> str:
    """Get the help text for the CLI.

    Returns:
        Help text string

    **Validates: Requirements 9.5**
    """
    parser = create_parser()
    return parser.format_help()
