"""
Property-based tests for wizard validation functions.

**Feature: deployment-wizard, Property 2: Region Validation**
**Feature: deployment-wizard, Property 3: Environment Validation**
**Validates: Requirements 3.2, 3.3, 4.2**
"""

import re
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from wizard.validators import (
    validate_region,
    validate_environment,
    validate_tag_key,
)


# Strategy for generating valid AWS region strings
valid_region_strategy = st.from_regex(r"^[a-z]{2}-[a-z]+-\d+$", fullmatch=True)

# Strategy for generating invalid region strings (don't match pattern)
invalid_region_strategy = st.one_of(
    st.text().filter(lambda x: not re.match(r"^[a-z]{2}-[a-z]+-\d+$", x)),
    st.just(""),
    st.just("US-EAST-1"),  # uppercase
    st.just("us_east_1"),  # underscores
    st.just("useast1"),  # no hyphens
    st.just("us-east"),  # missing number
)

# Strategy for generating valid environment strings
valid_environment_strategy = st.from_regex(r"^[a-zA-Z0-9-]+$", fullmatch=True).filter(
    lambda x: len(x) > 0
)

# Strategy for generating invalid environment strings
invalid_environment_strategy = st.one_of(
    st.just(""),
    st.text(
        alphabet=st.characters(
            blacklist_categories=("L", "N"), blacklist_characters="-"
        )
    ).filter(lambda x: len(x) > 0),
    st.just("dev@prod"),  # special character
    st.just("my_env"),  # underscore
    st.just("env name"),  # space
)


class TestRegionValidation:
    """Property tests for region validation.

    **Feature: deployment-wizard, Property 2: Region Validation**
    **Validates: Requirements 3.2, 3.3**
    """

    @given(valid_region_strategy)
    @settings(max_examples=100)
    def test_valid_regions_pass_validation(self, region: str):
        """
        Property test: For any string matching AWS region pattern, validation passes.

        **Feature: deployment-wizard, Property 2: Region Validation**
        **Validates: Requirements 3.2, 3.3**
        """
        assert validate_region(region) is True, (
            f"Valid region '{region}' should pass validation"
        )

    @given(st.text())
    @settings(max_examples=100)
    def test_invalid_regions_fail_validation(self, region: str):
        """
        Property test: For any string NOT matching AWS region pattern, validation fails.

        **Feature: deployment-wizard, Property 2: Region Validation**
        **Validates: Requirements 3.2, 3.3**
        """
        assume(not re.match(r"^[a-z]{2}-[a-z]+-\d+$", region))
        assert validate_region(region) is False, (
            f"Invalid region '{region}' should fail validation"
        )

    def test_known_valid_regions(self):
        """Test validation with known valid AWS regions."""
        valid_regions = [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-west-2",
            "eu-central-1",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
            "sa-east-1",
        ]
        for region in valid_regions:
            assert validate_region(region) is True, (
                f"Known region '{region}' should be valid"
            )

    def test_known_invalid_regions(self):
        """Test validation with known invalid region formats."""
        invalid_regions = [
            "",
            "US-EAST-1",  # uppercase
            "us_east_1",  # underscores
            "useast1",  # no hyphens
            "us-east",  # missing number
            "1-us-east",  # wrong order
            "us-east-1-a",  # extra suffix
            None,
        ]
        for region in invalid_regions:
            assert validate_region(region) is False, (
                f"Invalid region '{region}' should fail"
            )


class TestEnvironmentValidation:
    """Property tests for environment validation.

    **Feature: deployment-wizard, Property 3: Environment Validation**
    **Validates: Requirements 4.2**
    """

    @given(valid_environment_strategy)
    @settings(max_examples=100)
    def test_valid_environments_pass_validation(self, env: str):
        """
        Property test: For any string with only alphanumeric chars and hyphens, validation passes.

        **Feature: deployment-wizard, Property 3: Environment Validation**
        **Validates: Requirements 4.2**
        """
        assert validate_environment(env) is True, (
            f"Valid environment '{env}' should pass validation"
        )

    @given(st.text())
    @settings(max_examples=100)
    def test_invalid_environments_fail_validation(self, env: str):
        """
        Property test: For any string with invalid characters, validation fails.

        **Feature: deployment-wizard, Property 3: Environment Validation**
        **Validates: Requirements 4.2**
        """
        assume(not re.match(r"^[a-zA-Z0-9-]+$", env))
        assert validate_environment(env) is False, (
            f"Invalid environment '{env}' should fail validation"
        )

    def test_known_valid_environments(self):
        """Test validation with known valid environment names."""
        valid_envs = [
            "dev",
            "staging",
            "prod",
            "production",
            "my-env",
            "env-1",
            "Dev",
            "PROD",
            "test-env-123",
        ]
        for env in valid_envs:
            assert validate_environment(env) is True, (
                f"Known environment '{env}' should be valid"
            )

    def test_known_invalid_environments(self):
        """Test validation with known invalid environment names."""
        invalid_envs = [
            "",
            "my_env",  # underscore
            "my env",  # space
            "dev@prod",  # special character
            "env.name",  # dot
            "env/name",  # slash
            None,
        ]
        for env in invalid_envs:
            assert validate_environment(env) is False, (
                f"Invalid environment '{env}' should fail"
            )


class TestTagKeyValidation:
    """Tests for tag key validation.

    **Validates: Requirements 5.2**
    """

    @given(st.text(min_size=1).filter(lambda x: len(x.strip()) > 0))
    @settings(max_examples=100)
    def test_non_empty_tag_keys_pass_validation(self, key: str):
        """
        Property test: For any non-empty string (after stripping), validation passes.

        **Validates: Requirements 5.2**
        """
        assert validate_tag_key(key) is True, (
            f"Non-empty tag key '{key}' should pass validation"
        )

    def test_empty_tag_keys_fail_validation(self):
        """Test that empty tag keys fail validation."""
        invalid_keys = [
            "",
            "   ",
            "\t",
            "\n",
            "  \t\n  ",
            None,
        ]
        for key in invalid_keys:
            assert validate_tag_key(key) is False, f"Empty tag key '{key}' should fail"

    def test_valid_tag_keys(self):
        """Test validation with known valid tag keys."""
        valid_keys = [
            "Name",
            "Environment",
            "Project",
            "my-tag",
            "tag_with_underscore",
            "123",
            "a",
        ]
        for key in valid_keys:
            assert validate_tag_key(key) is True, f"Valid tag key '{key}' should pass"
