"""
Main entry point for the AWS Security Baseline Deployment Wizard.

This module orchestrates all wizard components to provide both interactive
and non-interactive deployment configuration experiences.

**Validates: Requirements 10.1, 10.2, 10.3**
"""

import sys
from typing import Optional

from rich.console import Console

from wizard.cli import parse_args, has_cli_args, build_config_from_args
from wizard.display import display_banner, display_summary, display_next_steps
from wizard.generator import generate_tfvars
from wizard.models import WizardConfig
from wizard.prompts import (
    select_modules,
    select_region,
    select_environment,
    configure_tags,
)


# Default output path for terraform.tfvars
DEFAULT_OUTPUT_PATH = "terraform.tfvars"


class WizardError(Exception):
    """Base exception for wizard errors."""

    pass


class InvalidInputError(WizardError):
    """Exception raised for invalid user input."""

    pass


class FileGenerationError(WizardError):
    """Exception raised when file generation fails."""

    pass


class DependencyError(WizardError):
    """Exception raised when required dependencies are missing."""

    pass


def check_dependencies() -> None:
    """Check that required dependencies are available.

    Raises:
        DependencyError: If required packages are not installed.

    **Validates: Requirements 10.3**
    """
    try:
        import rich  # noqa: F401
    except ImportError:
        raise DependencyError(
            "Required package 'rich' not found. Install with: pip install rich"
        )


def run_interactive_mode(console: Console) -> Optional[WizardConfig]:
    """Run the wizard in interactive mode.

    Guides the user through all configuration steps interactively:
    1. Module selection
    2. Region configuration
    3. Environment configuration
    4. Tag configuration
    5. Summary and confirmation

    Args:
        console: Rich Console instance for output.

    Returns:
        WizardConfig if user confirms, None if user cancels.

    **Validates: Requirements 2.1-2.5, 3.1-3.4, 4.1-4.2, 5.1-5.4, 6.1-6.4**
    """
    while True:
        # Step 1: Module selection
        modules = select_modules(console)

        # Step 2: Region configuration
        region = select_region(console)

        # Step 3: Environment configuration
        environment = select_environment(console)

        # Step 4: Tag configuration
        tags = configure_tags(environment, console)

        # Build configuration
        config = WizardConfig(
            modules=modules,
            region=region,
            environment=environment,
            tags=tags,
        )

        # Step 5: Summary and confirmation
        console.print()
        if display_summary(config, console):
            return config
        else:
            console.print("\n[yellow]Restarting configuration...[/yellow]\n")
            # Loop back to restart configuration


def run_non_interactive_mode(console: Console) -> WizardConfig:
    """Run the wizard in non-interactive mode using CLI arguments.

    Builds configuration from command-line arguments without user prompts.

    Args:
        console: Rich Console instance for output.

    Returns:
        WizardConfig built from CLI arguments.

    **Validates: Requirements 9.1-9.5**
    """
    args = parse_args()
    config = build_config_from_args(args)

    # Display what was configured
    console.print("\n[bold cyan]Non-Interactive Mode[/bold cyan]")
    console.print(f"  Region: {config.region}")
    console.print(f"  Environment: {config.environment}")

    enabled_modules = [name for name, enabled in config.modules.items() if enabled]
    if enabled_modules:
        console.print(f"  Modules: {', '.join(enabled_modules)}")
    else:
        console.print("  Modules: None selected")

    console.print(f"  Tags: {len(config.tags)} configured")

    return config


def main(output_path: str = DEFAULT_OUTPUT_PATH) -> int:
    """Main entry point for the deployment wizard.

    Orchestrates all wizard components in the correct order:
    1. Check dependencies
    2. Display banner
    3. Run interactive or non-interactive mode
    4. Generate terraform.tfvars
    5. Display next steps

    Args:
        output_path: Path for the generated terraform.tfvars file.

    Returns:
        Exit code (0 for success, non-zero for errors).

    **Validates: Requirements 10.1, 10.2, 10.3**
    """
    console = Console()

    try:
        # Check dependencies
        check_dependencies()

        # Display banner
        display_banner(console)

        # Determine mode based on CLI arguments
        args = parse_args()

        if has_cli_args(args):
            # Non-interactive mode
            config = run_non_interactive_mode(console)
        else:
            # Interactive mode
            config = run_interactive_mode(console)

            if config is None:
                console.print("\n[yellow]Configuration cancelled.[/yellow]")
                return 1

        # Generate terraform.tfvars
        success = generate_tfvars(config, output_path, console)

        if not success:
            console.print("\n[red]Failed to generate configuration file.[/red]")
            return 1

        # Display next steps
        display_next_steps(output_path, console)

        return 0

    except DependencyError as e:
        console.print(f"\n[red]Dependency Error:[/red] {e}")
        return 1

    except InvalidInputError as e:
        console.print(f"\n[red]Invalid Input:[/red] {e}")
        return 1

    except FileGenerationError as e:
        console.print(f"\n[red]File Generation Error:[/red] {e}")
        console.print("[dim]Check file permissions and try again.[/dim]")
        return 1

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Wizard cancelled by user.[/yellow]")
        return 130

    except Exception as e:
        console.print(f"\n[red]Unexpected Error:[/red] {e}")
        console.print(
            "[dim]Please report this issue at: https://github.com/jsredmond/aws-security-baseline/issues[/dim]"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
