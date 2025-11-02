"""Main CLI interface using Click and Rich."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from envwizard import __version__
from envwizard.core import EnvWizard

console = Console()


def print_banner() -> None:
    """Print the envwizard banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███████╗███╗   ██╗██╗   ██╗██╗    ██╗██╗███████╗      ║
    ║   ██╔════╝████╗  ██║██║   ██║██║    ██║██║╚══███╔╝      ║
    ║   █████╗  ██╔██╗ ██║██║   ██║██║ █╗ ██║██║  ███╔╝       ║
    ║   ██╔══╝  ██║╚██╗██║╚██╗ ██╔╝██║███╗██║██║ ███╔╝        ║
    ║   ███████╗██║ ╚████║ ╚████╔╝ ╚███╔███╔╝██║███████╗      ║
    ║   ╚══════╝╚═╝  ╚═══╝  ╚═══╝   ╚══╝╚══╝ ╚═╝╚══════╝      ║
    ║                                                           ║
    ║          Smart Environment Setup Tool                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print(f"                          v{__version__}\n", style="dim")


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """
    envwizard - Smart environment setup tool.

    One command to create virtual envs, install deps, and configure .env intelligently.
    """
    if version:
        console.print(f"envwizard version {__version__}", style="bold green")
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        print_banner()
        console.print(
            "Use [bold cyan]envwizard --help[/bold cyan] to see available commands.\n"
        )


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Project directory path (default: current directory)",
)
@click.option(
    "--venv-name",
    "-n",
    default="venv",
    help="Virtual environment name (default: venv)",
)
@click.option(
    "--no-install",
    is_flag=True,
    help="Skip dependency installation",
)
@click.option(
    "--no-dotenv",
    is_flag=True,
    help="Skip .env file generation",
)
@click.option(
    "--python-version",
    help="Specific Python version to use (e.g., 3.11)",
)
def init(
    path: Optional[Path],
    venv_name: str,
    no_install: bool,
    no_dotenv: bool,
    python_version: Optional[str],
) -> None:
    """
    Initialize a complete development environment.

    This command will:
    - Detect your project type and frameworks
    - Create a virtual environment
    - Install dependencies (if found)
    - Generate .env files with smart defaults
    """
    print_banner()

    project_path = path or Path.cwd()
    console.print(f"\n[bold]Project path:[/bold] {project_path}\n")

    wizard = EnvWizard(project_path)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Analyze project
        task = progress.add_task("[cyan]Analyzing project...", total=None)
        project_info = wizard.get_project_info()
        progress.update(task, completed=True)

    # Display project information
    _display_project_info(project_info)

    # Confirm before proceeding
    if not click.confirm("\n[bold]Proceed with setup?[/bold]", default=True):
        console.print("[yellow]Setup cancelled.[/yellow]")
        return

    console.print()

    # Perform setup
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Setting up environment...", total=None)

        results = wizard.setup(
            venv_name=venv_name,
            install_deps=not no_install,
            create_dotenv=not no_dotenv,
        )

        progress.update(task, completed=True)

    # Display results
    _display_results(results)


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Project directory path",
)
def detect(path: Optional[Path]) -> None:
    """
    Detect project type and frameworks without making any changes.
    """
    print_banner()

    project_path = path or Path.cwd()
    console.print(f"\n[bold]Analyzing project at:[/bold] {project_path}\n")

    wizard = EnvWizard(project_path)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Detecting project type...", total=None)
        project_info = wizard.get_project_info()
        progress.update(task, completed=True)

    _display_project_info(project_info)


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Project directory path",
)
@click.option(
    "--name",
    "-n",
    default="venv",
    help="Virtual environment name",
)
@click.option(
    "--python-version",
    help="Specific Python version to use",
)
def create_venv(path: Optional[Path], name: str, python_version: Optional[str]) -> None:
    """
    Create a virtual environment only.
    """
    project_path = path or Path.cwd()
    wizard = EnvWizard(project_path)

    console.print(f"\n[bold]Creating virtual environment '{name}'...[/bold]\n")

    success, message, venv_path = wizard.create_venv_only(name, python_version)

    if success:
        console.print(f"[green]✓[/green] {message}\n")
        if venv_path:
            activation_cmd = wizard.venv_manager.get_activation_command(venv_path)
            console.print(
                Panel(
                    f"[bold cyan]{activation_cmd}[/bold cyan]",
                    title="[bold]Activation Command[/bold]",
                    border_style="green",
                )
            )
    else:
        console.print(f"[red]✗[/red] {message}", style="bold red")
        sys.exit(1)


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Project directory path",
)
def create_dotenv(path: Optional[Path]) -> None:
    """
    Generate .env files only.
    """
    project_path = path or Path.cwd()
    wizard = EnvWizard(project_path)

    console.print("\n[bold]Generating .env files...[/bold]\n")

    success, message = wizard.create_dotenv_only()

    if success:
        console.print(f"[green]✓[/green] {message}\n")
        console.print(
            Panel(
                "[yellow]⚠[/yellow]  Remember to update the placeholder values in .env!",
                border_style="yellow",
            )
        )
    else:
        console.print(f"[red]✗[/red] {message}", style="bold red")
        sys.exit(1)


def _display_project_info(project_info: dict) -> None:
    """Display detected project information."""
    # Create main info table
    table = Table(title="[bold]Project Information[/bold]", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    # Add detected frameworks
    if project_info.get("frameworks"):
        frameworks = ", ".join(project_info["frameworks"])
        table.add_row("Frameworks", frameworks)
    else:
        table.add_row("Frameworks", "[dim]None detected[/dim]")

    # Add dependency files
    dep_files = []
    if project_info.get("has_requirements"):
        dep_files.append("requirements.txt")
    if project_info.get("has_pyproject"):
        dep_files.append("pyproject.toml")
    if project_info.get("has_pipfile"):
        dep_files.append("Pipfile")
    if project_info.get("has_setup_py"):
        dep_files.append("setup.py")

    if dep_files:
        table.add_row("Dependency Files", ", ".join(dep_files))
    else:
        table.add_row("Dependency Files", "[dim]None found[/dim]")

    # Add Python version
    if project_info.get("python_version"):
        table.add_row("Python Version", project_info["python_version"])

    console.print(table)
    console.print()

    # Show detected files tree
    if project_info.get("detected_files"):
        tree = Tree("[bold]Detected Project Files[/bold]")
        for file in project_info["detected_files"][:10]:  # Show first 10
            tree.add(f"[dim]{file}[/dim]")
        if len(project_info["detected_files"]) > 10:
            tree.add(f"[dim]... and {len(project_info['detected_files']) - 10} more[/dim]")
        console.print(tree)
        console.print()


def _display_results(results: dict) -> None:
    """Display setup results."""
    console.print("\n[bold]Setup Results[/bold]\n")

    # Virtual environment
    if results.get("venv_created"):
        console.print("[green]✓[/green] Virtual environment created")
    else:
        console.print("[yellow]○[/yellow] Virtual environment (skipped or already exists)")

    # Dependencies
    if results.get("deps_installed"):
        console.print("[green]✓[/green] Dependencies installed")
    elif "No dependency file" in " ".join(results.get("messages", [])):
        console.print("[yellow]○[/yellow] Dependencies (no dependency file found)")
    else:
        console.print("[red]✗[/red] Dependencies installation failed")

    # .env files
    if results.get("dotenv_created"):
        console.print("[green]✓[/green] .env files created")
    else:
        console.print("[yellow]○[/yellow] .env files (skipped or already exist)")

    console.print()

    # Show activation command
    if results.get("activation_command"):
        console.print(
            Panel(
                f"[bold cyan]{results['activation_command']}[/bold cyan]",
                title="[bold]Next Step: Activate Virtual Environment[/bold]",
                border_style="green",
            )
        )
        console.print()

    # Show warnings or messages
    if results.get("dotenv_created"):
        console.print(
            Panel(
                "[yellow]⚠[/yellow]  Don't forget to update the values in .env before running your application!",
                border_style="yellow",
            )
        )
        console.print()

    # Show errors if any
    if results.get("errors"):
        console.print("[bold red]Errors:[/bold red]")
        for error in results["errors"]:
            console.print(f"  [red]•[/red] {error}")
        console.print()


if __name__ == "__main__":
    cli()
