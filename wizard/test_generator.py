"""
Property-based tests for wizard tfvars generator.

**Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
**Validates: Requirements 7.1, 7.2, 7.3**
"""

import os
import tempfile
from io import StringIO

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from rich.console import Console

from wizard.generator import (
    generate_tfvars_content,
    parse_tfvars_content,
    generate_tfvars,
)
from wizard.models import AVAILABLE_MODULES, EXPECTED_MODULE_NAMES, WizardConfig


# Strategy for generating valid module selections (all 8 modules)
module_selection_strategy = st.fixed_dictionaries(
    {name: st.booleans() for name in EXPECTED_MODULE_NAMES}
)

# Strategy for generating valid AWS regions
region_strategy = st.from_regex(r"[a-z]{2}-[a-z]+-[0-9]+", fullmatch=True)

# Strategy for generating valid environments (alphanumeric and hyphens)
environment_strategy = st.from_regex(r"[a-zA-Z][a-zA-Z0-9-]*", fullmatch=True).filter(
    lambda s: 1 <= len(s) <= 20
)

# Strategy for generating valid tag keys (non-empty, no special HCL chars)
tag_key_strategy = st.from_regex(r"[a-zA-Z][a-zA-Z0-9_]*", fullmatch=True).filter(
    lambda s: 1 <= len(s) <= 30
)

# Strategy for generating valid tag values (no newlines or unescaped quotes)
tag_value_strategy = st.text(
    alphabet=st.characters(blacklist_characters='\n\r'),
    min_size=0,
    max_size=50
)

# Strategy for generating valid tags dictionary
tags_strategy = st.dictionaries(
    keys=tag_key_strategy,
    values=tag_value_strategy,
    min_size=1,
    max_size=5
)

# Strategy for generating valid WizardConfig
wizard_config_strategy = st.builds(
    WizardConfig,
    modules=module_selection_strategy,
    region=region_strategy,
    environment=environment_strategy,
    tags=tags_strategy
)


class TestTfvarsRoundTrip:
    """Property tests for tfvars generation round-trip.
    
    **Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
    **Validates: Requirements 7.1, 7.2, 7.3**
    """

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_round_trip_preserves_region(self, config: WizardConfig):
        """
        Property test: For any valid WizardConfig, generating and parsing
        preserves the region value.
        
        **Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
        **Validates: Requirements 7.1, 7.2, 7.3**
        """
        content = generate_tfvars_content(config)
        parsed = parse_tfvars_content(content)
        
        assert parsed.region == config.region, (
            f"Region should be preserved: expected '{config.region}', got '{parsed.region}'"
        )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_round_trip_preserves_environment(self, config: WizardConfig):
        """
        Property test: For any valid WizardConfig, generating and parsing
        preserves the environment value.
        
        **Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
        **Validates: Requirements 7.1, 7.2, 7.3**
        """
        content = generate_tfvars_content(config)
        parsed = parse_tfvars_content(content)
        
        assert parsed.environment == config.environment, (
            f"Environment should be preserved: expected '{config.environment}', got '{parsed.environment}'"
        )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_round_trip_preserves_modules(self, config: WizardConfig):
        """
        Property test: For any valid WizardConfig, generating and parsing
        preserves all module enabled/disabled states.
        
        **Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
        **Validates: Requirements 7.1, 7.2, 7.3**
        """
        content = generate_tfvars_content(config)
        parsed = parse_tfvars_content(content)
        
        for module_name in EXPECTED_MODULE_NAMES:
            expected = config.modules.get(module_name, False)
            actual = parsed.modules.get(module_name, False)
            assert actual == expected, (
                f"Module '{module_name}' should be preserved: expected {expected}, got {actual}"
            )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_round_trip_preserves_tags(self, config: WizardConfig):
        """
        Property test: For any valid WizardConfig, generating and parsing
        preserves all tags exactly.
        
        **Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
        **Validates: Requirements 7.1, 7.2, 7.3**
        """
        content = generate_tfvars_content(config)
        parsed = parse_tfvars_content(content)
        
        assert parsed.tags == config.tags, (
            f"Tags should be preserved: expected {config.tags}, got {parsed.tags}"
        )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_enabled_modules_have_true_in_output(self, config: WizardConfig):
        """
        Property test: For any enabled module, the output contains 'enable_X = true'.
        
        **Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
        **Validates: Requirements 7.2**
        """
        content = generate_tfvars_content(config)
        
        for module in AVAILABLE_MODULES:
            if config.modules.get(module.name, False):
                expected_line = f"{module.var_name} = true"
                assert expected_line in content, (
                    f"Enabled module '{module.name}' should have '{expected_line}' in output"
                )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_disabled_modules_have_false_in_output(self, config: WizardConfig):
        """
        Property test: For any disabled module, the output contains 'enable_X = false'.
        
        **Feature: deployment-wizard, Property 6: tfvars Generation Round-Trip**
        **Validates: Requirements 7.2**
        """
        content = generate_tfvars_content(config)
        
        for module in AVAILABLE_MODULES:
            if not config.modules.get(module.name, False):
                expected_line = f"{module.var_name} = false"
                assert expected_line in content, (
                    f"Disabled module '{module.name}' should have '{expected_line}' in output"
                )


class TestTfvarsGeneration:
    """Unit tests for tfvars file generation.
    
    **Validates: Requirements 7.1, 7.4**
    """

    def test_generate_tfvars_creates_file(self):
        """Test that generate_tfvars creates a file successfully.
        
        **Validates: Requirements 7.1, 7.4**
        """
        config = WizardConfig(
            modules={name: True for name in EXPECTED_MODULE_NAMES},
            region="us-east-1",
            environment="test",
            tags={"Environment": "test", "ManagedBy": "Terraform"}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tfvars', delete=False) as f:
            temp_path = f.name
        
        try:
            # Remove the file so we can test creation
            os.unlink(temp_path)
            
            console = Console(file=StringIO(), force_terminal=True)
            result = generate_tfvars(config, temp_path, console, force_overwrite=True)
            
            assert result is True, "generate_tfvars should return True on success"
            assert os.path.exists(temp_path), "File should be created"
            
            # Verify content
            with open(temp_path, 'r') as f:
                content = f.read()
            
            assert 'environment = "test"' in content
            assert 'aws_region  = "us-east-1"' in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_generate_tfvars_displays_path(self):
        """Test that generate_tfvars displays the output path.
        
        **Validates: Requirements 7.4**
        """
        config = WizardConfig(
            modules={name: False for name in EXPECTED_MODULE_NAMES},
            region="eu-west-1",
            environment="prod",
            tags={"Environment": "prod"}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tfvars', delete=False) as f:
            temp_path = f.name
        
        try:
            output = StringIO()
            console = Console(file=output, force_terminal=True)
            result = generate_tfvars(config, temp_path, console, force_overwrite=True)
            
            assert result is True
            printed_output = output.getvalue()
            assert temp_path in printed_output or "Generated" in printed_output
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_generated_content_has_valid_hcl_syntax(self):
        """Test that generated content uses valid HCL syntax.
        
        **Validates: Requirements 7.2**
        """
        config = WizardConfig(
            modules={"cloudtrail": True, "config": False, "guardduty": True,
                     "detective": False, "securityhub": True, "accessanalyzer": False,
                     "inspector": True, "macie": False},
            region="ap-southeast-1",
            environment="staging",
            tags={"Environment": "staging", "Team": "Security"}
        )
        
        content = generate_tfvars_content(config)
        
        # Check HCL syntax patterns
        assert 'environment = "staging"' in content, "String values should be quoted"
        assert 'aws_region  = "ap-southeast-1"' in content, "Region should be quoted"
        assert 'enable_cloudtrail = true' in content, "Boolean true should be lowercase"
        assert 'enable_config = false' in content, "Boolean false should be lowercase"
        assert 'common_tags = {' in content, "Tags block should use HCL map syntax"
        assert '}' in content, "Tags block should be closed"

    def test_tags_with_special_characters(self):
        """Test that tags with special characters are properly escaped.
        
        **Validates: Requirements 7.2**
        """
        config = WizardConfig(
            modules={name: True for name in EXPECTED_MODULE_NAMES},
            region="us-east-1",
            environment="test",
            tags={"Description": 'Value with "quotes"', "Normal": "simple"}
        )
        
        content = generate_tfvars_content(config)
        parsed = parse_tfvars_content(content)
        
        # The quotes should be escaped and then unescaped correctly
        assert parsed.tags["Description"] == 'Value with "quotes"'
        assert parsed.tags["Normal"] == "simple"
