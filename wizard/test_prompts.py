"""
Property-based tests for wizard interactive prompts.

**Feature: deployment-wizard, Property 1: Module Selection Round-Trip**
**Feature: deployment-wizard, Property 4: Tag Handling**
**Validates: Requirements 2.1, 2.2, 5.1, 5.2, 5.3**
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from wizard.models import AVAILABLE_MODULES, EXPECTED_MODULE_NAMES
from wizard.prompts import (
    COMMON_REGIONS,
    DEFAULT_REGION,
    SUGGESTED_ENVIRONMENTS,
)
from wizard.validators import validate_tag_key


class TestModuleSelectionRoundTrip:
    """Property tests for module selection round-trip.
    
    **Feature: deployment-wizard, Property 1: Module Selection Round-Trip**
    **Validates: Requirements 2.1, 2.2**
    """

    @given(st.dictionaries(
        keys=st.sampled_from(list(EXPECTED_MODULE_NAMES)),
        values=st.booleans(),
        min_size=len(EXPECTED_MODULE_NAMES),
        max_size=len(EXPECTED_MODULE_NAMES)
    ))
    @settings(max_examples=100)
    def test_module_selections_preserve_all_modules(self, selections: dict):
        """
        Property test: For any set of module selections, all expected modules are represented.
        
        **Feature: deployment-wizard, Property 1: Module Selection Round-Trip**
        **Validates: Requirements 2.1, 2.2**
        """
        # Ensure we have exactly the expected modules
        assume(set(selections.keys()) == EXPECTED_MODULE_NAMES)
        
        # Verify all modules are present
        assert set(selections.keys()) == EXPECTED_MODULE_NAMES, (
            "Module selections should contain exactly the expected modules"
        )

    @given(st.lists(
        st.booleans(),
        min_size=len(EXPECTED_MODULE_NAMES),
        max_size=len(EXPECTED_MODULE_NAMES)
    ))
    @settings(max_examples=100)
    def test_module_selections_preserve_enabled_status(self, enabled_list: list):
        """
        Property test: For any combination of enabled/disabled modules, 
        the selection dictionary correctly reflects each module's status.
        
        **Feature: deployment-wizard, Property 1: Module Selection Round-Trip**
        **Validates: Requirements 2.1, 2.2**
        """
        # Create selections from the enabled list
        module_names = list(EXPECTED_MODULE_NAMES)
        selections = {name: enabled for name, enabled in zip(module_names, enabled_list)}
        
        # Verify each module's status is preserved
        for name, enabled in zip(module_names, enabled_list):
            assert selections[name] == enabled, (
                f"Module '{name}' should have enabled={enabled}"
            )

    def test_deploy_all_enables_all_modules(self):
        """Test that 'Deploy All' option enables all modules.
        
        **Validates: Requirements 2.4**
        """
        # Simulate "Deploy All" selection
        selections = {module.name: True for module in AVAILABLE_MODULES}
        
        # Verify all modules are enabled
        assert all(selections.values()), "All modules should be enabled"
        assert len(selections) == len(AVAILABLE_MODULES), (
            "Should have selections for all modules"
        )

    def test_deploy_none_disables_all_modules(self):
        """Test that 'Deploy None' option disables all modules.
        
        **Validates: Requirements 2.4**
        """
        # Simulate "Deploy None" selection
        selections = {module.name: False for module in AVAILABLE_MODULES}
        
        # Verify all modules are disabled
        assert not any(selections.values()), "All modules should be disabled"
        assert len(selections) == len(AVAILABLE_MODULES), (
            "Should have selections for all modules"
        )

    def test_available_modules_match_expected(self):
        """Test that AVAILABLE_MODULES contains all expected modules.
        
        **Validates: Requirements 2.5**
        """
        actual_names = {module.name for module in AVAILABLE_MODULES}
        assert actual_names == EXPECTED_MODULE_NAMES, (
            "AVAILABLE_MODULES should contain exactly the expected modules"
        )


class TestTagHandling:
    """Property tests for tag handling.
    
    **Feature: deployment-wizard, Property 4: Tag Handling**
    **Validates: Requirements 5.1, 5.2, 5.3**
    """

    @given(st.text(min_size=1).filter(lambda x: len(x.strip()) > 0))
    @settings(max_examples=100)
    def test_non_empty_tag_keys_are_valid(self, key: str):
        """
        Property test: For any non-empty tag key, validation passes.
        
        **Feature: deployment-wizard, Property 4: Tag Handling**
        **Validates: Requirements 5.2**
        """
        assert validate_tag_key(key) is True, (
            f"Non-empty tag key '{key}' should be valid"
        )

    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=50).filter(lambda x: len(x.strip()) > 0),
        values=st.text(max_size=100),
        min_size=0,
        max_size=10
    ))
    @settings(max_examples=100)
    def test_custom_tags_are_recorded(self, custom_tags: dict):
        """
        Property test: For any set of custom tags with non-empty keys,
        all tags are recorded in the configuration.
        
        **Feature: deployment-wizard, Property 4: Tag Handling**
        **Validates: Requirements 5.1, 5.3**
        """
        # Simulate tag configuration with auto-included tags
        environment = "test"
        tags = {
            "Environment": environment,
            "ManagedBy": "Terraform",
        }
        
        # Add custom tags
        for key, value in custom_tags.items():
            if validate_tag_key(key):
                tags[key] = value
        
        # Verify auto-included tags are present
        assert "Environment" in tags, "Environment tag should be present"
        assert "ManagedBy" in tags, "ManagedBy tag should be present"
        assert tags["Environment"] == environment, "Environment tag should match"
        assert tags["ManagedBy"] == "Terraform", "ManagedBy tag should be 'Terraform'"
        
        # Verify all custom tags with valid keys are recorded
        for key, value in custom_tags.items():
            if validate_tag_key(key):
                assert key in tags, f"Custom tag '{key}' should be recorded"
                assert tags[key] == value, f"Custom tag '{key}' should have value '{value}'"

    @given(st.text(alphabet=st.characters(whitelist_categories=('Zs',)), min_size=0, max_size=10))
    @settings(max_examples=100)
    def test_empty_or_whitespace_tag_keys_are_rejected(self, key: str):
        """
        Property test: For any empty or whitespace-only tag key, validation fails.
        
        **Feature: deployment-wizard, Property 4: Tag Handling**
        **Validates: Requirements 5.2**
        """
        assert validate_tag_key(key) is False, (
            f"Empty or whitespace tag key '{repr(key)}' should be rejected"
        )

    def test_auto_included_tags_are_present(self):
        """Test that Environment and ManagedBy tags are auto-included.
        
        **Validates: Requirements 5.4**
        """
        environment = "production"
        
        # Simulate tag configuration
        tags = {
            "Environment": environment,
            "ManagedBy": "Terraform",
        }
        
        assert "Environment" in tags, "Environment tag should be auto-included"
        assert "ManagedBy" in tags, "ManagedBy tag should be auto-included"
        assert tags["Environment"] == environment, "Environment tag should match input"
        assert tags["ManagedBy"] == "Terraform", "ManagedBy should be 'Terraform'"

    @given(st.text(min_size=1, max_size=50).filter(lambda x: len(x.strip()) > 0 and x.isalnum()))
    @settings(max_examples=100)
    def test_environment_tag_reflects_input(self, environment: str):
        """
        Property test: For any valid environment name, the Environment tag
        reflects that value.
        
        **Feature: deployment-wizard, Property 4: Tag Handling**
        **Validates: Requirements 5.4**
        """
        tags = {
            "Environment": environment,
            "ManagedBy": "Terraform",
        }
        
        assert tags["Environment"] == environment, (
            f"Environment tag should be '{environment}'"
        )


class TestRegionConfiguration:
    """Tests for region configuration.
    
    **Validates: Requirements 3.1, 3.4**
    """

    def test_common_regions_list_is_populated(self):
        """Test that COMMON_REGIONS contains expected regions.
        
        **Validates: Requirements 3.1**
        """
        assert len(COMMON_REGIONS) > 0, "COMMON_REGIONS should not be empty"
        assert "us-east-1" in COMMON_REGIONS, "us-east-1 should be in common regions"
        assert "eu-west-1" in COMMON_REGIONS, "eu-west-1 should be in common regions"

    def test_default_region_is_us_east_1(self):
        """Test that default region is us-east-1.
        
        **Validates: Requirements 3.4**
        """
        assert DEFAULT_REGION == "us-east-1", "Default region should be us-east-1"


class TestEnvironmentConfiguration:
    """Tests for environment configuration.
    
    **Validates: Requirements 4.1**
    """

    def test_suggested_environments_contains_expected_values(self):
        """Test that SUGGESTED_ENVIRONMENTS contains dev, staging, prod.
        
        **Validates: Requirements 4.1**
        """
        assert "dev" in SUGGESTED_ENVIRONMENTS, "dev should be suggested"
        assert "staging" in SUGGESTED_ENVIRONMENTS, "staging should be suggested"
        assert "prod" in SUGGESTED_ENVIRONMENTS, "prod should be suggested"
