"""
Unit tests for wizard display components.

**Validates: Requirements 1.1, 1.3**
"""

import pytest
from io import StringIO

from rich.console import Console

from wizard.display import (
    display_banner,
    display_next_steps,
    get_banner_content,
    get_next_steps_content,
    GITHUB_URL,
    ASCII_BANNER,
)


class TestBannerContent:
    """Unit tests for banner content.
    
    **Validates: Requirements 1.1, 1.3**
    """

    def test_banner_contains_aws_security_baseline_text(self):
        """Verify banner contains 'AWS Security Baseline' text.
        
        **Validates: Requirements 1.1**
        """
        content = get_banner_content()
        assert "AWS Security Baseline" in content, (
            "Banner should contain 'AWS Security Baseline' text"
        )

    def test_banner_contains_github_url(self):
        """Verify banner contains GitHub URL.
        
        **Validates: Requirements 1.3**
        """
        content = get_banner_content()
        assert GITHUB_URL in content, (
            f"Banner should contain GitHub URL: {GITHUB_URL}"
        )

    def test_github_url_is_correct(self):
        """Verify the GitHub URL is the expected repository."""
        expected_url = "https://github.com/jsredmond/aws-security-baseline"
        assert GITHUB_URL == expected_url, (
            f"GitHub URL should be '{expected_url}', got '{GITHUB_URL}'"
        )

    def test_ascii_banner_contains_security_text(self):
        """Verify ASCII art contains security-related text."""
        # The ASCII art should spell out "Security" and "Baseline"
        assert "Security" in ASCII_BANNER or "___" in ASCII_BANNER, (
            "ASCII banner should contain recognizable art"
        )

    def test_display_banner_returns_content(self):
        """Verify display_banner returns content string."""
        # Use a console that writes to a string buffer
        console = Console(file=StringIO(), force_terminal=True)
        result = display_banner(console)
        
        assert result is not None, "display_banner should return content"
        assert "AWS Security Baseline" in result, (
            "Returned content should contain 'AWS Security Baseline'"
        )
        assert GITHUB_URL in result, (
            "Returned content should contain GitHub URL"
        )

    def test_display_banner_prints_to_console(self):
        """Verify display_banner prints to the console."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        
        display_banner(console)
        
        printed_output = output.getvalue()
        assert len(printed_output) > 0, "display_banner should print to console"
        # The panel title should be in the output
        assert "AWS Security Baseline" in printed_output or "Security" in printed_output, (
            "Console output should contain banner content"
        )

    def test_display_banner_without_console_argument(self):
        """Verify display_banner works without console argument."""
        # This should not raise an exception
        result = display_banner()
        assert result is not None, "display_banner should work without console argument"


from hypothesis import given, settings
from hypothesis import strategies as st

from wizard.models import AVAILABLE_MODULES, WizardConfig
from wizard.display import get_summary_content


# Strategy for generating valid module selections
module_names = [m.name for m in AVAILABLE_MODULES]
module_selection_strategy = st.fixed_dictionaries(
    {name: st.booleans() for name in module_names}
)

# Strategy for generating valid regions
region_strategy = st.from_regex(r"[a-z]{2}-[a-z]+-[0-9]+", fullmatch=True)

# Strategy for generating valid environments
environment_strategy = st.from_regex(r"[a-zA-Z0-9][a-zA-Z0-9-]*", fullmatch=True).filter(
    lambda s: len(s) <= 20
)

# Strategy for generating valid tag keys and values
tag_key_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="_-"),
    min_size=1,
    max_size=20
)
tag_value_strategy = st.text(min_size=1, max_size=50).filter(lambda s: s.strip() != "")

# Strategy for generating valid tags dictionary
tags_strategy = st.dictionaries(
    keys=tag_key_strategy,
    values=tag_value_strategy,
    min_size=0,
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


class TestSummaryCompleteness:
    """Property tests for configuration summary completeness.
    
    **Feature: deployment-wizard, Property 5: Configuration Summary Completeness**
    **Validates: Requirements 6.1, 6.2**
    """

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_summary_contains_all_module_names(self, config: WizardConfig):
        """
        Property test: For any WizardConfig, the summary contains all module display names.
        
        **Feature: deployment-wizard, Property 5: Configuration Summary Completeness**
        **Validates: Requirements 6.1, 6.2**
        """
        summary = get_summary_content(config)
        
        for module in AVAILABLE_MODULES:
            assert module.display_name in summary, (
                f"Summary should contain module '{module.display_name}'"
            )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_summary_contains_module_status(self, config: WizardConfig):
        """
        Property test: For any WizardConfig, the summary shows enabled/disabled status for each module.
        
        **Feature: deployment-wizard, Property 5: Configuration Summary Completeness**
        **Validates: Requirements 6.1, 6.2**
        """
        summary = get_summary_content(config)
        
        for module in AVAILABLE_MODULES:
            enabled = config.modules.get(module.name, False)
            expected_status = "Enabled" if enabled else "Disabled"
            # Check that the module line contains the correct status
            assert f"{module.display_name}: {expected_status}" in summary, (
                f"Summary should show '{module.display_name}' as '{expected_status}'"
            )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_summary_contains_region(self, config: WizardConfig):
        """
        Property test: For any WizardConfig, the summary contains the selected region.
        
        **Feature: deployment-wizard, Property 5: Configuration Summary Completeness**
        **Validates: Requirements 6.1, 6.2**
        """
        summary = get_summary_content(config)
        
        assert config.region in summary, (
            f"Summary should contain region '{config.region}'"
        )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_summary_contains_environment(self, config: WizardConfig):
        """
        Property test: For any WizardConfig, the summary contains the selected environment.
        
        **Feature: deployment-wizard, Property 5: Configuration Summary Completeness**
        **Validates: Requirements 6.1, 6.2**
        """
        summary = get_summary_content(config)
        
        assert config.environment in summary, (
            f"Summary should contain environment '{config.environment}'"
        )

    @given(config=wizard_config_strategy)
    @settings(max_examples=100)
    def test_summary_contains_all_tags(self, config: WizardConfig):
        """
        Property test: For any WizardConfig, the summary contains all configured tags.
        
        **Feature: deployment-wizard, Property 5: Configuration Summary Completeness**
        **Validates: Requirements 6.1, 6.2**
        """
        summary = get_summary_content(config)
        
        for key, value in config.tags.items():
            assert key in summary, (
                f"Summary should contain tag key '{key}'"
            )
            assert value in summary, (
                f"Summary should contain tag value '{value}'"
            )



class TestNextStepsContent:
    """Unit tests for next steps content.
    
    **Validates: Requirements 8.1, 8.2, 8.3**
    """

    def test_next_steps_contains_terraform_init(self):
        """Verify next steps contains terraform init command.
        
        **Validates: Requirements 8.1**
        """
        content = get_next_steps_content("terraform.tfvars")
        assert "terraform init" in content, (
            "Next steps should contain 'terraform init' command"
        )

    def test_next_steps_contains_terraform_plan(self):
        """Verify next steps contains terraform plan command.
        
        **Validates: Requirements 8.2**
        """
        content = get_next_steps_content("terraform.tfvars")
        assert "terraform plan" in content, (
            "Next steps should contain 'terraform plan' command"
        )

    def test_next_steps_contains_terraform_apply(self):
        """Verify next steps contains terraform apply command.
        
        **Validates: Requirements 8.2**
        """
        content = get_next_steps_content("terraform.tfvars")
        assert "terraform apply" in content, (
            "Next steps should contain 'terraform apply' command"
        )

    def test_next_steps_mentions_aws_credentials(self):
        """Verify next steps mentions AWS credentials configuration.
        
        **Validates: Requirements 8.3**
        """
        content = get_next_steps_content("terraform.tfvars")
        assert "AWS" in content and "credentials" in content.lower(), (
            "Next steps should mention AWS credentials"
        )

    def test_next_steps_mentions_aws_configure(self):
        """Verify next steps mentions aws configure command.
        
        **Validates: Requirements 8.3**
        """
        content = get_next_steps_content("terraform.tfvars")
        assert "aws configure" in content, (
            "Next steps should mention 'aws configure' command"
        )

    def test_next_steps_contains_output_path(self):
        """Verify next steps contains the output file path."""
        output_path = "custom/path/terraform.tfvars"
        content = get_next_steps_content(output_path)
        assert output_path in content, (
            f"Next steps should contain output path '{output_path}'"
        )

    def test_display_next_steps_returns_content(self):
        """Verify display_next_steps returns content string."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        result = display_next_steps("terraform.tfvars", console)
        
        assert result is not None, "display_next_steps should return content"
        assert "terraform init" in result, (
            "Returned content should contain 'terraform init'"
        )

    def test_display_next_steps_prints_to_console(self):
        """Verify display_next_steps prints to the console."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        
        display_next_steps("terraform.tfvars", console)
        
        printed_output = output.getvalue()
        assert len(printed_output) > 0, "display_next_steps should print to console"

    def test_display_next_steps_without_console_argument(self):
        """Verify display_next_steps works without console argument."""
        # This should not raise an exception
        result = display_next_steps("terraform.tfvars")
        assert result is not None, "display_next_steps should work without console argument"
