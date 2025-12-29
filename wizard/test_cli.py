"""
Property-based tests for CLI argument handling.

**Feature: deployment-wizard, Property 7: CLI Argument Handling**
**Validates: Requirements 9.1, 9.3, 9.4**
"""

import re
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from wizard.cli import (
    parse_args,
    build_config_from_args,
    parse_tag,
    validate_region_arg,
    validate_environment_arg,
    has_cli_args,
    get_help_text,
)
from wizard.models import AVAILABLE_MODULES, EXPECTED_MODULE_NAMES


# Strategy for generating valid AWS region strings
valid_region_strategy = st.from_regex(r"^[a-z]{2}-[a-z]+-\d+$", fullmatch=True)

# Strategy for generating valid environment strings
# Filter out values starting with '-' as argparse interprets them as flags
valid_environment_strategy = st.from_regex(r"^[a-zA-Z0-9-]+$", fullmatch=True).filter(
    lambda x: len(x) > 0 and not x.startswith('-')
)

# Strategy for generating valid tag key-value pairs
# Filter out keys starting with '-' as argparse interprets them as flags
valid_tag_key_strategy = st.text(min_size=1, max_size=50).filter(
    lambda x: len(x.strip()) > 0 and '=' not in x and not x.startswith('-')
)
valid_tag_value_strategy = st.text(max_size=100)


class TestCLIArgumentHandling:
    """Property tests for CLI argument handling.
    
    **Feature: deployment-wizard, Property 7: CLI Argument Handling**
    **Validates: Requirements 9.1, 9.3, 9.4**
    """

    @given(valid_region_strategy)
    @settings(max_examples=100)
    def test_region_argument_sets_config_region(self, region: str):
        """
        Property test: If --region is provided, WizardConfig.region SHALL equal that value.
        
        **Feature: deployment-wizard, Property 7: CLI Argument Handling**
        **Validates: Requirements 9.3**
        """
        args = parse_args(['--region', region])
        config = build_config_from_args(args)
        
        assert config.region == region, (
            f"Config region '{config.region}' should equal provided region '{region}'"
        )

    @given(valid_environment_strategy)
    @settings(max_examples=100)
    def test_env_argument_sets_config_environment(self, env: str):
        """
        Property test: If --env is provided, WizardConfig.environment SHALL equal that value.
        
        **Feature: deployment-wizard, Property 7: CLI Argument Handling**
        **Validates: Requirements 9.4**
        """
        args = parse_args(['--env', env])
        config = build_config_from_args(args)
        
        assert config.environment == env, (
            f"Config environment '{config.environment}' should equal provided env '{env}'"
        )

    def test_all_modules_flag_enables_all_modules(self):
        """
        Property test: If --all-modules is provided, all modules SHALL be enabled.
        
        **Feature: deployment-wizard, Property 7: CLI Argument Handling**
        **Validates: Requirements 9.1**
        """
        args = parse_args(['--all-modules'])
        config = build_config_from_args(args)
        
        # Verify all expected modules are enabled
        assert len(config.modules) == len(AVAILABLE_MODULES), (
            f"Expected {len(AVAILABLE_MODULES)} modules, got {len(config.modules)}"
        )
        
        for module in AVAILABLE_MODULES:
            assert module.name in config.modules, (
                f"Module '{module.name}' should be in config.modules"
            )
            assert config.modules[module.name] is True, (
                f"Module '{module.name}' should be enabled"
            )

    @given(
        region=valid_region_strategy,
        env=valid_environment_strategy,
    )
    @settings(max_examples=100)
    def test_combined_arguments_set_all_values(self, region: str, env: str):
        """
        Property test: Combined arguments should set all corresponding config values.
        
        **Feature: deployment-wizard, Property 7: CLI Argument Handling**
        **Validates: Requirements 9.1, 9.3, 9.4**
        """
        args = parse_args(['--all-modules', '--region', region, '--env', env])
        config = build_config_from_args(args)
        
        assert config.region == region
        assert config.environment == env
        assert all(config.modules.get(m.name, False) for m in AVAILABLE_MODULES)

    @given(
        key=valid_tag_key_strategy,
        value=valid_tag_value_strategy,
    )
    @settings(max_examples=100)
    def test_tag_argument_adds_to_config_tags(self, key: str, value: str):
        """
        Property test: Tags provided via --tag should appear in config.tags.
        
        **Feature: deployment-wizard, Property 7: CLI Argument Handling**
        **Validates: Requirements 9.1**
        """
        tag_string = f"{key}={value}"
        args = parse_args(['--tag', tag_string])
        config = build_config_from_args(args)
        
        assert key in config.tags, (
            f"Tag key '{key}' should be in config.tags"
        )
        assert config.tags[key] == value, (
            f"Tag value for '{key}' should be '{value}', got '{config.tags[key]}'"
        )


class TestCLITagParsing:
    """Tests for tag parsing functionality."""

    def test_valid_tag_parsing(self):
        """Test parsing valid KEY=VALUE tags."""
        valid_tags = [
            ("Name=MyResource", ("Name", "MyResource")),
            ("Environment=prod", ("Environment", "prod")),
            ("Key=", ("Key", "")),  # Empty value is valid
            ("Key=Value=With=Equals", ("Key", "Value=With=Equals")),  # Value can contain =
        ]
        for tag_string, expected in valid_tags:
            result = parse_tag(tag_string)
            assert result == expected, f"parse_tag('{tag_string}') should return {expected}"

    def test_invalid_tag_parsing(self):
        """Test that invalid tags raise ArgumentTypeError."""
        import argparse
        
        invalid_tags = [
            "NoEqualsSign",
            "=ValueOnly",
            "",
        ]
        for tag_string in invalid_tags:
            with pytest.raises(argparse.ArgumentTypeError):
                parse_tag(tag_string)


class TestCLIValidation:
    """Tests for CLI argument validation."""

    def test_invalid_region_raises_error(self):
        """Test that invalid region format raises error."""
        import argparse
        
        invalid_regions = [
            "invalid",
            "US-EAST-1",
            "us_east_1",
        ]
        for region in invalid_regions:
            with pytest.raises(argparse.ArgumentTypeError):
                validate_region_arg(region)

    def test_invalid_environment_raises_error(self):
        """Test that invalid environment format raises error."""
        import argparse
        
        invalid_envs = [
            "env@name",
            "env name",
            "",
        ]
        for env in invalid_envs:
            with pytest.raises(argparse.ArgumentTypeError):
                validate_environment_arg(env)


class TestCLIHelperFunctions:
    """Tests for CLI helper functions."""

    def test_has_cli_args_with_no_args(self):
        """Test has_cli_args returns False when no args provided."""
        args = parse_args([])
        assert has_cli_args(args) is False

    def test_has_cli_args_with_all_modules(self):
        """Test has_cli_args returns True when --all-modules provided."""
        args = parse_args(['--all-modules'])
        assert has_cli_args(args) is True

    def test_has_cli_args_with_region(self):
        """Test has_cli_args returns True when --region provided."""
        args = parse_args(['--region', 'us-east-1'])
        assert has_cli_args(args) is True

    def test_has_cli_args_with_env(self):
        """Test has_cli_args returns True when --env provided."""
        args = parse_args(['--env', 'dev'])
        assert has_cli_args(args) is True

    def test_has_cli_args_with_tag(self):
        """Test has_cli_args returns True when --tag provided."""
        args = parse_args(['--tag', 'Key=Value'])
        assert has_cli_args(args) is True

    def test_get_help_text_contains_expected_content(self):
        """Test that help text contains expected information."""
        help_text = get_help_text()
        
        assert "--all-modules" in help_text
        assert "--region" in help_text
        assert "--env" in help_text
        assert "--tag" in help_text
        assert "-h" in help_text or "--help" in help_text


class TestCLIDefaults:
    """Tests for CLI default values."""

    def test_default_region_when_not_provided(self):
        """Test that default region is us-east-1 when not provided."""
        args = parse_args([])
        config = build_config_from_args(args)
        
        assert config.region == "us-east-1"

    def test_default_environment_when_not_provided(self):
        """Test that default environment is dev when not provided."""
        args = parse_args([])
        config = build_config_from_args(args)
        
        assert config.environment == "dev"

    def test_auto_included_tags(self):
        """Test that Environment and ManagedBy tags are auto-included."""
        args = parse_args(['--env', 'prod'])
        config = build_config_from_args(args)
        
        assert "Environment" in config.tags
        assert config.tags["Environment"] == "prod"
        assert "ManagedBy" in config.tags
        assert config.tags["ManagedBy"] == "Terraform"
