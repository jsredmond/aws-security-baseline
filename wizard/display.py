"""
Display components for the AWS Security Baseline Deployment Wizard.

This module provides functions for rendering the terminal UI including
the welcome banner, configuration summary, and next steps guidance.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.text import Text

from wizard.models import AVAILABLE_MODULES, WizardConfig


# GitHub repository URL
GITHUB_URL = "https://github.com/jsredmond/aws-security-baseline"

# ASCII art banner
ASCII_BANNER = r"""
    ___        ______    ____                       _ _         
   / \ \      / / ___|  / ___|  ___  ___ _   _ _ __(_) |_ _   _ 
  / _ \ \ /\ / /\___ \  \___ \ / _ \/ __| | | | '__| | __| | | |
 / ___ \ V  V /  ___) |  ___) |  __/ (__| |_| | |  | | |_| |_| |
/_/   \_\_/\_/  |____/  |____/ \___|\___|\__,_|_|  |_|\__|\__, |
                                                          |___/ 
    ____                 _ _            
   | __ )  __ _ ___  ___| (_)_ __   ___ 
   |  _ \ / _` / __|/ _ \ | | '_ \ / _ \
   | |_) | (_| \__ \  __/ | | | | |  __/
   |____/ \__,_|___/\___|_|_|_| |_|\___|
"""


def display_banner(console: Console | None = None) -> str:
    """Display the ASCII art banner with project info.

    Renders a professional branded welcome screen with:
    - ASCII art "AWS Security Baseline" banner
    - Box-style border around the content
    - GitHub repository link
    - Brief description of the tool's purpose
    - Colored output for visual appeal

    Args:
        console: Optional Rich Console instance. If None, creates a new one.

    Returns:
        The rendered banner content as a string (for testing purposes).
    """
    if console is None:
        console = Console()

    # Create the banner text with styling
    banner_text = Text()
    banner_text.append(ASCII_BANNER, style="bold cyan")
    banner_text.append("\n")
    banner_text.append(
        "Deploy AWS security services with confidence\n\n", style="italic white"
    )
    banner_text.append("GitHub: ", style="dim")
    banner_text.append(GITHUB_URL, style="bold blue underline")

    # Create a panel with box border
    panel = Panel(
        banner_text,
        title="[bold green]AWS Security Baseline[/bold green]",
        subtitle="[dim]Deployment Wizard[/dim]",
        border_style="green",
        padding=(1, 2),
    )

    # Print the panel
    console.print(panel)

    # Return content for testing
    return f"AWS Security Baseline\n{ASCII_BANNER}\n{GITHUB_URL}"


def get_banner_content() -> str:
    """Get the banner content as a string without printing.

    This function is useful for testing to verify banner content
    without side effects.

    Returns:
        String containing the banner text including title and GitHub URL.
    """
    return f"AWS Security Baseline\n{ASCII_BANNER}\n{GITHUB_URL}"


def display_summary(config: WizardConfig, console: Console | None = None) -> bool:
    """Display configuration summary and prompt for confirmation.

    Shows a comprehensive summary of all user selections including:
    - All enabled/disabled modules in a table
    - Selected AWS region
    - Environment name
    - All configured tags

    Args:
        config: The WizardConfig containing all user selections.
        console: Optional Rich Console instance. If None, creates a new one.

    Returns:
        True if user confirms the configuration, False to restart.

    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    if console is None:
        console = Console()

    # Create modules table
    modules_table = Table(
        title="Security Modules", show_header=True, header_style="bold cyan"
    )
    modules_table.add_column("Module", style="white")
    modules_table.add_column("Status", justify="center")
    modules_table.add_column("Description", style="dim")

    # Add each module to the table
    for module in AVAILABLE_MODULES:
        enabled = config.modules.get(module.name, False)
        status = (
            "[bold green]✓ Enabled[/bold green]"
            if enabled
            else "[dim red]✗ Disabled[/dim red]"
        )
        modules_table.add_row(module.display_name, status, module.description)

    # Create settings table
    settings_table = Table(
        title="Deployment Settings", show_header=True, header_style="bold cyan"
    )
    settings_table.add_column("Setting", style="white")
    settings_table.add_column("Value", style="bold yellow")

    settings_table.add_row("AWS Region", config.region)
    settings_table.add_row("Environment", config.environment)

    # Create tags table
    tags_table = Table(
        title="Resource Tags", show_header=True, header_style="bold cyan"
    )
    tags_table.add_column("Key", style="white")
    tags_table.add_column("Value", style="bold yellow")

    for key, value in config.tags.items():
        tags_table.add_row(key, value)

    # Display all tables
    console.print()
    console.print(Panel("[bold]Configuration Summary[/bold]", border_style="green"))
    console.print()
    console.print(modules_table)
    console.print()
    console.print(settings_table)
    console.print()
    console.print(tags_table)
    console.print()

    # Prompt for confirmation
    confirmed = Confirm.ask(
        "[bold]Proceed with this configuration?[/bold]", default=True, console=console
    )

    return confirmed


def get_summary_content(config: WizardConfig) -> str:
    """Get the summary content as a string without printing.

    This function is useful for testing to verify summary content
    without side effects or user interaction.

    Args:
        config: The WizardConfig containing all user selections.

    Returns:
        String containing the summary text including all modules,
        region, environment, and tags.
    """
    lines = []

    # Add modules section
    lines.append("Security Modules:")
    for module in AVAILABLE_MODULES:
        enabled = config.modules.get(module.name, False)
        status = "Enabled" if enabled else "Disabled"
        lines.append(f"  {module.display_name}: {status}")

    # Add settings section
    lines.append("")
    lines.append("Deployment Settings:")
    lines.append(f"  Region: {config.region}")
    lines.append(f"  Environment: {config.environment}")

    # Add tags section
    lines.append("")
    lines.append("Resource Tags:")
    for key, value in config.tags.items():
        lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def display_next_steps(output_path: str, console: Console | None = None) -> str:
    """Display next steps guidance after configuration generation.

    Shows clear instructions for completing the deployment including:
    - terraform init command
    - terraform plan command
    - terraform apply command
    - Reminder about AWS credentials configuration

    Args:
        output_path: Path to the generated terraform.tfvars file.
        console: Optional Rich Console instance. If None, creates a new one.

    Returns:
        The rendered next steps content as a string (for testing purposes).

    Requirements: 8.1, 8.2, 8.3
    """
    if console is None:
        console = Console()

    # Build the next steps content
    next_steps_text = Text()

    # Success message
    next_steps_text.append("✓ Configuration saved to: ", style="bold green")
    next_steps_text.append(f"{output_path}\n\n", style="bold white")

    # AWS credentials reminder
    next_steps_text.append("⚠ AWS Credentials\n", style="bold yellow")
    next_steps_text.append(
        "  Ensure your AWS credentials are configured before running Terraform.\n",
        style="white",
    )
    next_steps_text.append("  You can configure credentials using:\n", style="dim")
    next_steps_text.append("    • AWS CLI: ", style="dim")
    next_steps_text.append("aws configure\n", style="cyan")
    next_steps_text.append("    • Environment variables: ", style="dim")
    next_steps_text.append("AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY\n", style="cyan")
    next_steps_text.append("    • IAM role (for EC2/ECS)\n\n", style="dim")

    # Terraform commands
    next_steps_text.append("📋 Next Steps\n", style="bold blue")
    next_steps_text.append("  Run the following commands to deploy:\n\n", style="white")

    next_steps_text.append("  1. Initialize Terraform:\n", style="white")
    next_steps_text.append("     terraform init\n\n", style="bold cyan")

    next_steps_text.append("  2. Preview the changes:\n", style="white")
    next_steps_text.append("     terraform plan\n\n", style="bold cyan")

    next_steps_text.append("  3. Apply the configuration:\n", style="white")
    next_steps_text.append("     terraform apply\n", style="bold cyan")

    # Create a panel with the content
    panel = Panel(
        next_steps_text,
        title="[bold green]Deployment Ready[/bold green]",
        border_style="green",
        padding=(1, 2),
    )

    # Print the panel
    console.print()
    console.print(panel)
    console.print()

    # Return content for testing
    return get_next_steps_content(output_path)


def get_next_steps_content(output_path: str) -> str:
    """Get the next steps content as a string without printing.

    This function is useful for testing to verify next steps content
    without side effects.

    Args:
        output_path: Path to the generated terraform.tfvars file.

    Returns:
        String containing the next steps text including terraform commands
        and AWS credentials reminder.
    """
    lines = [
        f"Configuration saved to: {output_path}",
        "",
        "AWS Credentials",
        "Ensure your AWS credentials are configured before running Terraform.",
        "aws configure",
        "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY",
        "",
        "Next Steps",
        "terraform init",
        "terraform plan",
        "terraform apply",
    ]

    return "\n".join(lines)
