#!/usr/bin/env python3
"""
AWS Security Baseline Deployment Wizard

A CLI tool for configuring and deploying AWS security services.

Usage:
    python wizard.py                    # Interactive mode
    python wizard.py --all-modules      # Enable all modules
    python wizard.py --region us-west-2 # Specify region
    python wizard.py --help             # Show help

For more information, visit:
    https://github.com/jsredmond/aws-security-baseline
"""

import sys

from wizard.main import main


if __name__ == "__main__":
    sys.exit(main())
