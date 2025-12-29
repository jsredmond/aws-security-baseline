"""
Property-based tests for wizard data models.

**Feature: deployment-wizard, Property: Module registry contains exactly 8 expected modules**
**Validates: Requirements 2.5**
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from wizard.models import (
    AVAILABLE_MODULES,
    EXPECTED_MODULE_NAMES,
    ModuleInfo,
    WizardConfig,
)


class TestModuleRegistryCompleteness:
    """Property tests for module registry completeness.
    
    **Feature: deployment-wizard, Property: Module registry contains exactly 8 expected modules**
    **Validates: Requirements 2.5**
    """

    def test_registry_contains_exactly_8_modules(self):
        """Verify the registry contains exactly 8 modules."""
        assert len(AVAILABLE_MODULES) == 8

    def test_registry_contains_all_expected_modules(self):
        """Verify all expected module names are present in the registry."""
        actual_names = {module.name for module in AVAILABLE_MODULES}
        assert actual_names == EXPECTED_MODULE_NAMES

    def test_all_modules_have_required_fields(self):
        """Verify all modules have non-empty required fields."""
        for module in AVAILABLE_MODULES:
            assert module.name, f"Module missing name"
            assert module.display_name, f"Module {module.name} missing display_name"
            assert module.description, f"Module {module.name} missing description"
            assert module.var_name, f"Module {module.name} missing var_name"

    def test_all_var_names_follow_convention(self):
        """Verify all var_names follow the enable_<name> convention."""
        for module in AVAILABLE_MODULES:
            expected_var_name = f"enable_{module.name}"
            assert module.var_name == expected_var_name, (
                f"Module {module.name} has var_name '{module.var_name}' "
                f"but expected '{expected_var_name}'"
            )

    def test_no_duplicate_module_names(self):
        """Verify there are no duplicate module names."""
        names = [module.name for module in AVAILABLE_MODULES]
        assert len(names) == len(set(names)), "Duplicate module names found"

    def test_no_duplicate_var_names(self):
        """Verify there are no duplicate var_names."""
        var_names = [module.var_name for module in AVAILABLE_MODULES]
        assert len(var_names) == len(set(var_names)), "Duplicate var_names found"

    @given(st.sampled_from(list(EXPECTED_MODULE_NAMES)))
    @settings(max_examples=100)
    def test_each_expected_module_exists_in_registry(self, module_name: str):
        """
        Property test: For any expected module name, it exists in the registry.
        
        **Feature: deployment-wizard, Property: Module registry contains exactly 8 expected modules**
        **Validates: Requirements 2.5**
        """
        actual_names = {module.name for module in AVAILABLE_MODULES}
        assert module_name in actual_names, (
            f"Expected module '{module_name}' not found in registry"
        )

    @given(st.sampled_from(AVAILABLE_MODULES))
    @settings(max_examples=100)
    def test_each_registry_module_is_expected(self, module: ModuleInfo):
        """
        Property test: For any module in the registry, it is in the expected set.
        
        **Feature: deployment-wizard, Property: Module registry contains exactly 8 expected modules**
        **Validates: Requirements 2.5**
        """
        assert module.name in EXPECTED_MODULE_NAMES, (
            f"Registry module '{module.name}' is not in expected modules"
        )
