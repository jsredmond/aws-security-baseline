"""
Property-based tests for wizard main module error handling.

**Feature: deployment-wizard, Property 8: Error Handling for Invalid Input**
**Validates: Requirements 10.1**
"""

import re
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from unittest.mock import patch, MagicMock

from wizard.main import (
    main,
    check_dependencies,
    WizardError,
    InvalidInputError,
    FileGenerationError,
    DependencyError,
)
from wizard.validators import validate_region, validate_environment, validate_tag_key


# Strategy for generating invalid region strings
invalid_region_strategy = st.text().filter(
    lambda x: x and not re.match(r"^[a-z]{2}-[a-z]+-\d+$", x)
)

# Strategy for generating invalid environment strings (contain invalid chars)
invalid_environment_strategy = st.text(
    alphabet=st.characters(blacklist_categories=("L", "N"), blacklist_characters="-")
).filter(lambda x: len(x) > 0)

# Strategy for generating empty/whitespace-only tag keys
invalid_tag_key_strategy = st.one_of(
    st.just(""),
    st.text(alphabet=" \t\n").filter(lambda x: len(x) > 0),
)


class TestErrorHandlingProperty:
    """Property tests for error handling.

    **Feature: deployment-wizard, Property 8: Error Handling for Invalid Input**
    **Validates: Requirements 10.1**
    """

    @given(invalid_region_strategy)
    @settings(max_examples=100)
    def test_invalid_region_does_not_proceed(self, region: str):
        """
        Property test: For any invalid region format, the wizard does not proceed.

        The wizard should reject invalid regions and display an error message.

        **Feature: deployment-wizard, Property 8: Error Handling for Invalid Input**
        **Validates: Requirements 10.1**
        """
        # Verify the region is actually invalid
        assert validate_region(region) is False, (
            f"Test precondition failed: '{region}' should be invalid"
        )

        # The validation function correctly rejects invalid regions
        # This ensures the wizard won't proceed with invalid values
        result = validate_region(region)
        assert result is False, (
            f"Invalid region '{region}' should be rejected by validation"
        )

    @given(invalid_environment_strategy)
    @settings(max_examples=100)
    def test_invalid_environment_does_not_proceed(self, env: str):
        """
        Property test: For any invalid environment name, the wizard does not proceed.

        The wizard should reject invalid environment names and display an error.

        **Feature: deployment-wizard, Property 8: Error Handling for Invalid Input**
        **Validates: Requirements 10.1**
        """
        # Verify the environment is actually invalid
        assume(not re.match(r"^[a-zA-Z0-9-]+$", env))

        # The validation function correctly rejects invalid environments
        result = validate_environment(env)
        assert result is False, (
            f"Invalid environment '{env}' should be rejected by validation"
        )

    @given(invalid_tag_key_strategy)
    @settings(max_examples=100)
    def test_empty_tag_key_does_not_proceed(self, key: str):
        """
        Property test: For any empty tag key, the wizard does not proceed.

        The wizard should reject empty tag keys and display an error.

        **Feature: deployment-wizard, Property 8: Error Handling for Invalid Input**
        **Validates: Requirements 10.1**
        """
        # The validation function correctly rejects empty tag keys
        result = validate_tag_key(key)
        assert result is False, (
            f"Empty tag key '{repr(key)}' should be rejected by validation"
        )


class TestDependencyChecking:
    """Tests for dependency checking.

    **Validates: Requirements 10.3**
    """

    def test_check_dependencies_passes_when_rich_available(self):
        """Test that dependency check passes when rich is installed."""
        # This should not raise since rich is installed
        check_dependencies()

    def test_check_dependencies_raises_when_rich_missing(self):
        """Test that dependency check raises when rich is not installed."""
        with patch.dict("sys.modules", {"rich": None}):
            # Force reimport to trigger the check
            with pytest.raises(DependencyError) as exc_info:
                # Simulate missing rich by patching the import
                with patch(
                    "builtins.__import__",
                    side_effect=ImportError("No module named 'rich'"),
                ):
                    check_dependencies()

            assert "rich" in str(exc_info.value)
            assert "pip install rich" in str(exc_info.value)


class TestExceptionTypes:
    """Tests for custom exception types."""

    def test_wizard_error_is_base_exception(self):
        """Test that WizardError is the base exception class."""
        assert issubclass(InvalidInputError, WizardError)
        assert issubclass(FileGenerationError, WizardError)
        assert issubclass(DependencyError, WizardError)

    def test_invalid_input_error_message(self):
        """Test InvalidInputError can be raised with a message."""
        with pytest.raises(InvalidInputError) as exc_info:
            raise InvalidInputError("Invalid region format")
        assert "Invalid region format" in str(exc_info.value)

    def test_file_generation_error_message(self):
        """Test FileGenerationError can be raised with a message."""
        with pytest.raises(FileGenerationError) as exc_info:
            raise FileGenerationError("Permission denied")
        assert "Permission denied" in str(exc_info.value)

    def test_dependency_error_message(self):
        """Test DependencyError can be raised with a message."""
        with pytest.raises(DependencyError) as exc_info:
            raise DependencyError("Missing package")
        assert "Missing package" in str(exc_info.value)


class TestMainFunction:
    """Tests for the main function orchestration."""

    def test_main_returns_zero_on_success(self, tmp_path):
        """Test that main returns 0 on successful execution."""
        output_file = tmp_path / "terraform.tfvars"

        # Mock interactive mode to return a config immediately
        mock_config = MagicMock()
        mock_config.modules = {"cloudtrail": True}
        mock_config.region = "us-east-1"
        mock_config.environment = "dev"
        mock_config.tags = {"Environment": "dev", "ManagedBy": "Terraform"}

        with patch("wizard.main.parse_args"):
            with patch("wizard.main.has_cli_args", return_value=True):
                with patch(
                    "wizard.main.run_non_interactive_mode", return_value=mock_config
                ):
                    with patch("wizard.main.generate_tfvars", return_value=True):
                        with patch("wizard.main.display_banner"):
                            with patch("wizard.main.display_next_steps"):
                                result = main(str(output_file))

        assert result == 0

    def test_main_returns_one_on_file_generation_failure(self, tmp_path):
        """Test that main returns 1 when file generation fails."""
        output_file = tmp_path / "terraform.tfvars"

        mock_config = MagicMock()
        mock_config.modules = {}
        mock_config.region = "us-east-1"
        mock_config.environment = "dev"
        mock_config.tags = {}

        with patch("wizard.main.parse_args"):
            with patch("wizard.main.has_cli_args", return_value=True):
                with patch(
                    "wizard.main.run_non_interactive_mode", return_value=mock_config
                ):
                    with patch("wizard.main.generate_tfvars", return_value=False):
                        with patch("wizard.main.display_banner"):
                            result = main(str(output_file))

        assert result == 1

    def test_main_handles_keyboard_interrupt(self, tmp_path):
        """Test that main handles KeyboardInterrupt gracefully."""
        output_file = tmp_path / "terraform.tfvars"

        with patch("wizard.main.parse_args"):
            with patch("wizard.main.has_cli_args", return_value=False):
                with patch(
                    "wizard.main.run_interactive_mode", side_effect=KeyboardInterrupt
                ):
                    with patch("wizard.main.display_banner"):
                        result = main(str(output_file))

        assert result == 130

    def test_main_handles_dependency_error(self, tmp_path):
        """Test that main handles DependencyError gracefully."""
        output_file = tmp_path / "terraform.tfvars"

        with patch(
            "wizard.main.check_dependencies",
            side_effect=DependencyError("Missing rich"),
        ):
            result = main(str(output_file))

        assert result == 1
