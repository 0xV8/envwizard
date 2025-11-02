"""Main CLI interface using Click and Rich."""

import sys
import traceback
from pathlib import Path
from subprocess import CalledProcessError
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

# Global debug flag
DEBUG_MODE = False


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


def handle_error(error: Exception, command_name: str = "command") -> None:
    """
    Display user-friendly error messages.

    Args:
        error: The exception that was raised
        command_name: Name of the command that failed
    """
    # Create error title
    error_title = f"[bold red]Error in '{command_name}' command[/bold red]"

    # Determine user-friendly message based on error type
    if isinstance(error, ValueError):
        error_msg = str(error)

        # Path validation errors
        if "Invalid project path" in error_msg or "Access to" in error_msg:
            title = "Security Validation Error"
            if "/etc" in error_msg:
                message = (
                    "[red]Access to /etc is not allowed for security reasons.[/red]\n\n"
                    "EnvWizard protects against path traversal attacks by blocking access to system directories.\n\n"
                    "[bold]Suggestion:[/bold] Please specify a valid project directory:\n"
                    "  [cyan]envwizard init --path=/path/to/your/project[/cyan]\n"
                    "  [cyan]envwizard init  # uses current directory[/cyan]"
                )
            elif "/sys" in error_msg or "/proc" in error_msg or "/root" in error_msg:
                message = (
                    "[red]Access to system directories is not allowed for security reasons.[/red]\n\n"
                    "EnvWizard only works with user project directories.\n\n"
                    "[bold]Suggestion:[/bold] Use a directory in your home folder or workspace:\n"
                    "  [cyan]envwizard init --path=~/projects/myapp[/cyan]"
                )
            elif "null bytes" in error_msg:
                message = (
                    "[red]Invalid path: Path contains invalid characters.[/red]\n\n"
                    "[bold]Suggestion:[/bold] Please provide a valid directory path."
                )
            elif "Invalid output filename" in error_msg:
                message = (
                    "[red]Invalid filename detected in .env generation.[/red]\n\n"
                    "The filename contains path separators or attempts path traversal.\n\n"
                    "[bold]Suggestion:[/bold] Use the default .env filename or a simple name without paths."
                )
            else:
                title = "Path Validation Error"
                message = f"[red]{error_msg}[/red]\n\n[bold]Suggestion:[/bold] Ensure you're using a valid directory path."

        # Python version validation errors
        elif "Invalid Python version format" in error_msg:
            message = (
                f"[red]{error_msg}[/red]\n\n"
                "[bold]Valid formats:[/bold]\n"
                "  [cyan]3.11[/cyan]     - Major.Minor\n"
                "  [cyan]3.11.2[/cyan]   - Major.Minor.Patch\n\n"
                "[bold]Example:[/bold]\n"
                "  [cyan]envwizard init --python-version 3.11[/cyan]"
            )
            title = "Invalid Python Version"

        # Package name validation errors
        elif "Invalid package name" in error_msg:
            message = (
                f"[red]{error_msg}[/red]\n\n"
                "[bold]Suggestion:[/bold] Check your requirements.txt for invalid package names.\n"
                "Package names should only contain alphanumeric characters and: . _ - [ ] >= < ~ !"
            )
            title = "Invalid Package Name"

        else:
            title = "Validation Error"
            message = f"[red]{error_msg}[/red]\n\n[bold]Suggestion:[/bold] Check your input parameters and try again."

    elif isinstance(error, FileNotFoundError):
        message = (
            f"[red]File or directory not found: {error.filename}[/red]\n\n"
            "[bold]Possible causes:[/bold]\n"
            "  • The path doesn't exist\n"
            "  • You don't have permission to access it\n"
            "  • There's a typo in the path\n\n"
            "[bold]Suggestion:[/bold]\n"
            "  • Check the path exists: [cyan]ls -la /path/to/directory[/cyan]\n"
            "  • Use absolute paths or verify current directory\n"
            "  • Ensure you have read permissions"
        )
        title = "File Not Found"

    elif isinstance(error, PermissionError):
        message = (
            f"[red]Permission denied: {error.filename if hasattr(error, 'filename') else 'unknown file'}[/red]\n\n"
            "[bold]Possible solutions:[/bold]\n"
            "  • Check file/directory permissions: [cyan]ls -la[/cyan]\n"
            "  • Ensure you own the directory: [cyan]chown -R $USER:$USER /path[/cyan]\n"
            "  • Run with appropriate permissions (avoid sudo with venvs)\n"
            "  • Choose a directory where you have write access"
        )
        title = "Permission Denied"

    elif isinstance(error, CalledProcessError):
        cmd = " ".join(error.cmd) if isinstance(error.cmd, list) else str(error.cmd)
        message = (
            f"[red]Command failed with exit code {error.returncode}[/red]\n\n"
            f"[bold]Command:[/bold] {cmd}\n\n"
        )

        # Add specific guidance for common subprocess failures
        if "pip" in cmd:
            message += (
                "[bold]Common pip issues:[/bold]\n"
                "  • Package not found on PyPI\n"
                "  • Incompatible version requirements\n"
                "  • Network connectivity issues\n\n"
                "[bold]Suggestions:[/bold]\n"
                "  • Check package names in requirements.txt\n"
                "  • Verify your internet connection\n"
                "  • Try manually: [cyan]pip install <package>[/cyan]"
            )
        elif "python" in cmd:
            message += (
                "[bold]Suggestions:[/bold]\n"
                "  • Ensure Python is installed\n"
                "  • Check Python version compatibility\n"
                "  • Verify the Python executable is in PATH"
            )

        title = "Command Execution Failed"

    elif isinstance(error, OSError):
        message = (
            f"[red]Operating system error: {error}[/red]\n\n"
            "[bold]Possible causes:[/bold]\n"
            "  • Disk space full\n"
            "  • Too many open files\n"
            "  • File system errors\n\n"
            "[bold]Suggestions:[/bold]\n"
            "  • Check disk space: [cyan]df -h[/cyan]\n"
            "  • Close unnecessary programs\n"
            "  • Try a different directory"
        )
        title = "System Error"

    elif isinstance(error, KeyboardInterrupt):
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)  # Standard exit code for SIGINT

    else:
        # Generic error
        message = (
            f"[red]{type(error).__name__}: {error}[/red]\n\n"
            "[bold]Suggestion:[/bold] This is an unexpected error. "
            "Use [cyan]--debug[/cyan] flag to see full details."
        )
        title = "Unexpected Error"

    # Display the error panel
    console.print()
    console.print(Panel(message, title=title, border_style="red", padding=(1, 2)))

    # Add debug hint
    if not DEBUG_MODE:
        console.print(
            "\n[dim]Use [cyan]--debug[/cyan] flag to see full stack trace:[/dim]",
            style="dim"
        )
        console.print(
            f"[dim]  envwizard --debug {command_name} [options][/dim]\n",
            style="dim"
        )

    # Show stack trace in debug mode
    if DEBUG_MODE:
        console.print("\n[bold yellow]Debug Information:[/bold yellow]")
        console.print(Panel(
            traceback.format_exc(),
            title="[bold]Stack Trace[/bold]",
            border_style="yellow",
            padding=(1, 2)
        ))


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--debug", is_flag=True, help="Show full error stack traces")
@click.pass_context
def cli(ctx: click.Context, version: bool, debug: bool) -> None:
    """
    envwizard - Smart environment setup tool.

    One command to create virtual envs, install deps, and configure .env intelligently.
    """
    global DEBUG_MODE
    DEBUG_MODE = debug

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
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts (non-interactive mode for CI/CD)",
)
@click.pass_context
def init(
    ctx: click.Context,
    path: Optional[Path],
    venv_name: str,
    no_install: bool,
    no_dotenv: bool,
    python_version: Optional[str],
    yes: bool,
) -> None:
    """
    Initialize a complete development environment.

    This command will:
    - Detect your project type and frameworks
    - Create a virtual environment
    - Install dependencies (if found)
    - Generate .env files with smart defaults
    """
    try:
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

        # Confirm before proceeding (skip if --yes flag is set)
        if not yes:
            if not click.confirm("\n[bold]Proceed with setup?[/bold]", default=True):
                console.print("[yellow]Setup cancelled.[/yellow]")
                return
        else:
            console.print("\n[dim]Non-interactive mode: skipping confirmation[/dim]")

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

    except Exception as e:
        handle_error(e, "init")
        sys.exit(1)


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Project directory path",
)
@click.pass_context
def detect(ctx: click.Context, path: Optional[Path]) -> None:
    """
    Detect project type and frameworks without making any changes.
    """
    try:
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

    except Exception as e:
        handle_error(e, "detect")
        sys.exit(1)


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
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts (non-interactive mode for CI/CD)",
)
@click.pass_context
def create_venv(
    ctx: click.Context,
    path: Optional[Path],
    name: str,
    python_version: Optional[str],
    yes: bool,
) -> None:
    """
    Create a virtual environment only.
    """
    try:
        project_path = path or Path.cwd()
        wizard = EnvWizard(project_path)

        console.print(f"\n[bold]Creating virtual environment '{name}'...[/bold]\n")

        if yes:
            console.print("[dim]Non-interactive mode: proceeding without confirmation[/dim]\n")

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

    except Exception as e:
        handle_error(e, "create-venv")
        sys.exit(1)


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Project directory path",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts (non-interactive mode for CI/CD)",
)
@click.pass_context
def create_dotenv(ctx: click.Context, path: Optional[Path], yes: bool) -> None:
    """
    Generate .env files only.
    """
    try:
        project_path = path or Path.cwd()
        wizard = EnvWizard(project_path)

        console.print("\n[bold]Generating .env files...[/bold]\n")

        if yes:
            console.print("[dim]Non-interactive mode: proceeding without confirmation[/dim]\n")

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

    except Exception as e:
        handle_error(e, "create-dotenv")
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
