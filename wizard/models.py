"""
Data models for the AWS Security Baseline Deployment Wizard.

This module defines the core data structures used throughout the wizard,
including module information and wizard configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ModuleInfo:
    """Information about an AWS security module.
    
    Attributes:
        name: Internal name (e.g., "cloudtrail")
        display_name: Display name (e.g., "CloudTrail")
        description: Brief description of the module
        var_name: Terraform variable name (e.g., "enable_cloudtrail")
    """
    name: str
    display_name: str
    description: str
    var_name: str


@dataclass
class WizardConfig:
    """Configuration collected by the wizard.
    
    Attributes:
        modules: Dictionary mapping module names to enabled status
        region: AWS region for deployment
        environment: Environment name (e.g., "dev", "staging", "prod")
        tags: Dictionary of resource tags
    """
    modules: Dict[str, bool] = field(default_factory=dict)
    region: str = "us-east-1"
    environment: str = "dev"
    tags: Dict[str, str] = field(default_factory=dict)


# Registry of all available security modules
AVAILABLE_MODULES: List[ModuleInfo] = [
    ModuleInfo(
        name="cloudtrail",
        display_name="CloudTrail",
        description="API logging and audit trail",
        var_name="enable_cloudtrail"
    ),
    ModuleInfo(
        name="config",
        display_name="AWS Config",
        description="Configuration change tracking",
        var_name="enable_config"
    ),
    ModuleInfo(
        name="guardduty",
        display_name="GuardDuty",
        description="Threat detection service",
        var_name="enable_guardduty"
    ),
    ModuleInfo(
        name="detective",
        display_name="Detective",
        description="Security investigation",
        var_name="enable_detective"
    ),
    ModuleInfo(
        name="securityhub",
        display_name="Security Hub",
        description="Central security dashboard",
        var_name="enable_securityhub"
    ),
    ModuleInfo(
        name="accessanalyzer",
        display_name="IAM Access Analyzer",
        description="External access analysis",
        var_name="enable_accessanalyzer"
    ),
    ModuleInfo(
        name="inspector",
        display_name="Inspector",
        description="Vulnerability scanning",
        var_name="enable_inspector"
    ),
    ModuleInfo(
        name="macie",
        display_name="Macie",
        description="Sensitive data discovery",
        var_name="enable_macie"
    ),
]


# Expected module names for validation
EXPECTED_MODULE_NAMES = {
    "cloudtrail",
    "config",
    "guardduty",
    "detective",
    "securityhub",
    "accessanalyzer",
    "inspector",
    "macie",
}
