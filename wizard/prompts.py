"""
Interactive prompts for the AWS Security Baseline Deployment Wizard.

This module provides interactive functions for collecting user input including
module selection, region configuration, environment selection, and tag configuration.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 5.1, 5.2, 5.3, 5.4**
"""

from typing import Dict

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from wizard.models import AVAILABLE_MODULES, ModuleInfo
from wizard.validators import validate_region, validate_environment, validate_tag_key


# Common AWS regions for selection
COMMON_REGIONS = [
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
]

# Default region
DEFAULT_REGION = "us-east-1"

# Suggested environments
SUGGESTED_ENVIRONMENTS = ["dev", "staging", "prod"]


def select_modules(console: Console | None = None) -> Dict[str, bool]:
    """Interactive module selection with Deploy All and Deploy None options.
    
    Presents all available security modules with descriptions and allows
    the user to select which modules to enable. Includes convenience options
    for deploying all or none of the modules.
    
    Args:
        console: Optional Rich Console instance. If None, creates a new one.
        
    Returns:
        Dictionary mapping module names to enabled status (True/False).
        
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    if console is None:
        console = Console()
    
    # Display available modules in a table
    console.print("\n[bold cyan]Available Security Modules[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Module", style="cyan")
    table.add_column("Description", style="white")
    
    for idx, module in enumerate(AVAILABLE_MODULES, 1):
        table.add_row(str(idx), module.display_name, module.description)
    
    console.print(table)
    console.print()
    
    # Show selection options
    console.print("[bold]Selection Options:[/bold]")
    console.print("  [green]A[/green] - Deploy All modules")
    console.print("  [red]N[/red] - Deploy None (skip all)")
    console.print("  [yellow]S[/yellow] - Select individually")
    console.print()
    
    # Get user choice
    choice = Prompt.ask(
        "How would you like to select modules?",
        choices=["A", "N", "S", "a", "n", "s"],
        default="A"
    ).upper()
    
    # Initialize selections
    selections: Dict[str, bool] = {}
    
    if choice == "A":
        # Deploy All
        for module in AVAILABLE_MODULES:
            selections[module.name] = True
        console.print("[green]✓ All modules selected for deployment[/green]")
        
    elif choice == "N":
        # Deploy None
        for module in AVAILABLE_MODULES:
            selections[module.name] = False
        console.print("[yellow]⚠ No modules selected for deployment[/yellow]")
        
    else:
        # Select individually
        console.print("\n[bold]Select modules individually:[/bold]")
        for module in AVAILABLE_MODULES:
            enabled = Confirm.ask(
                f"  Enable [cyan]{module.display_name}[/cyan] ({module.description})?",
                default=True
            )
            selections[module.name] = enabled
    
    return selections


def select_region(console: Console | None = None) -> str:
    """Interactive region selection with common regions list and custom option.
    
    Presents a list of common AWS regions and allows the user to select one
    or enter a custom region. Validates the region format.
    
    Args:
        console: Optional Rich Console instance. If None, creates a new one.
        
    Returns:
        Selected AWS region string.
        
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    """
    if console is None:
        console = Console()
    
    console.print("\n[bold cyan]AWS Region Configuration[/bold cyan]\n")
    
    # Display common regions
    console.print("[bold]Common AWS Regions:[/bold]")
    for idx, region in enumerate(COMMON_REGIONS, 1):
        default_marker = " [green](default)[/green]" if region == DEFAULT_REGION else ""
        console.print(f"  {idx:2}. {region}{default_marker}")
    console.print(f"  {len(COMMON_REGIONS) + 1:2}. [yellow]Enter custom region[/yellow]")
    console.print()
    
    while True:
        choice = Prompt.ask(
            "Select a region (number or region name)",
            default="1"
        )
        
        # Check if it's a number selection
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(COMMON_REGIONS):
                selected_region = COMMON_REGIONS[choice_num - 1]
                console.print(f"[green]✓ Selected region: {selected_region}[/green]")
                return selected_region
            elif choice_num == len(COMMON_REGIONS) + 1:
                # Custom region option
                custom_region = Prompt.ask("Enter custom region (e.g., eu-north-1)")
                if validate_region(custom_region):
                    console.print(f"[green]✓ Selected region: {custom_region}[/green]")
                    return custom_region
                else:
                    console.print("[red]Invalid region format. Expected format: us-east-1[/red]")
                    continue
            else:
                console.print(f"[red]Please enter a number between 1 and {len(COMMON_REGIONS) + 1}[/red]")
                continue
        except ValueError:
            # Not a number, treat as direct region input
            if validate_region(choice):
                console.print(f"[green]✓ Selected region: {choice}[/green]")
                return choice
            else:
                console.print("[red]Invalid region format. Expected format: us-east-1[/red]")
                continue


def select_environment(console: Console | None = None) -> str:
    """Interactive environment selection with dev/staging/prod suggestions.
    
    Prompts the user to select or enter an environment name. Validates that
    the environment name contains only alphanumeric characters and hyphens.
    
    Args:
        console: Optional Rich Console instance. If None, creates a new one.
        
    Returns:
        Selected environment name string.
        
    **Validates: Requirements 4.1, 4.2**
    """
    if console is None:
        console = Console()
    
    console.print("\n[bold cyan]Environment Configuration[/bold cyan]\n")
    
    # Display suggested environments
    console.print("[bold]Suggested Environments:[/bold]")
    for idx, env in enumerate(SUGGESTED_ENVIRONMENTS, 1):
        console.print(f"  {idx}. {env}")
    console.print("  Or enter a custom environment name")
    console.print()
    
    while True:
        choice = Prompt.ask(
            "Select or enter environment name",
            default="dev"
        )
        
        # Check if it's a number selection
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(SUGGESTED_ENVIRONMENTS):
                selected_env = SUGGESTED_ENVIRONMENTS[choice_num - 1]
                console.print(f"[green]✓ Selected environment: {selected_env}[/green]")
                return selected_env
            else:
                # Treat as custom input
                if validate_environment(choice):
                    console.print(f"[green]✓ Selected environment: {choice}[/green]")
                    return choice
                else:
                    console.print("[red]Invalid environment name. Use only letters, numbers, and hyphens.[/red]")
                    continue
        except ValueError:
            # Not a number, treat as direct environment input
            if validate_environment(choice):
                console.print(f"[green]✓ Selected environment: {choice}[/green]")
                return choice
            else:
                console.print("[red]Invalid environment name. Use only letters, numbers, and hyphens.[/red]")
                continue


def configure_tags(environment: str, console: Console | None = None) -> Dict[str, str]:
    """Interactive tag configuration with auto-included Environment and ManagedBy tags.
    
    Allows users to add custom key-value tag pairs. Automatically includes
    Environment and ManagedBy tags. Validates that tag keys are not empty.
    
    Args:
        environment: The environment name to use for the Environment tag.
        console: Optional Rich Console instance. If None, creates a new one.
        
    Returns:
        Dictionary of tag key-value pairs.
        
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    """
    if console is None:
        console = Console()
    
    console.print("\n[bold cyan]Tag Configuration[/bold cyan]\n")
    
    # Initialize with auto-included tags
    tags: Dict[str, str] = {
        "Environment": environment,
        "ManagedBy": "Terraform",
    }
    
    console.print("[bold]Auto-included tags:[/bold]")
    console.print(f"  • Environment = {environment}")
    console.print("  • ManagedBy = Terraform")
    console.print()
    
    # Ask if user wants to add custom tags
    add_custom = Confirm.ask("Would you like to add custom tags?", default=False)
    
    if add_custom:
        console.print("\n[dim]Enter tags as key=value pairs. Press Enter with empty key to finish.[/dim]\n")
        
        while True:
            key = Prompt.ask("Tag key (or press Enter to finish)", default="")
            
            if not key:
                break
            
            if not validate_tag_key(key):
                console.print("[red]Tag key cannot be empty or whitespace only.[/red]")
                continue
            
            value = Prompt.ask(f"Value for '{key}'", default="")
            tags[key] = value
            console.print(f"[green]✓ Added tag: {key} = {value}[/green]")
    
    # Display tag summary
    console.print("\n[bold]Tag Summary:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    
    for key, value in tags.items():
        table.add_row(key, value)
    
    console.print(table)
    
    return tags
