"""Core EnvWizard functionality."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from envwizard.detectors import DependencyDetector, FrameworkDetector, ProjectDetector
from envwizard.generators import DotEnvGenerator
from envwizard.logger import get_logger
from envwizard.venv import VirtualEnvManager

logger = get_logger(__name__)


def _validate_project_path(path: Path) -> Path:
    """
    Validate and resolve project path to prevent path traversal.

    Args:
        path: Path to validate

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path is invalid or attempts traversal outside allowed directories
    """
    try:
        # Resolve to absolute path, following symlinks
        resolved_path = path.resolve(strict=False)

        # Ensure it's a valid path (no null bytes, etc.)
        if "\x00" in str(resolved_path):
            raise ValueError("Path contains invalid null bytes")

        # Ensure path doesn't traverse to system directories
        # On macOS, /etc resolves to /private/etc, /var to /private/var, etc.
        # So we check both the original and resolved versions
        forbidden_paths = [
            Path("/etc"), Path("/sys"), Path("/proc"), Path("/root"),
            Path("/private/etc"), Path("/private/var/root"),
        ]

        for forbidden in forbidden_paths:
            # Resolve forbidden path to handle symlinks
            forbidden_resolved = forbidden.resolve(strict=False)

            # Check both resolved paths
            try:
                resolved_path.relative_to(forbidden_resolved)
                raise ValueError(f"Access to {forbidden} is not allowed")
            except ValueError as e:
                if "not allowed" in str(e):
                    raise
                # relative_to raised ValueError because path is not relative - this is OK
                pass

        return resolved_path
    except Exception as e:
        raise ValueError(f"Invalid project path: {e}")


class EnvWizard:
    """Main EnvWizard class for environment setup."""

    def __init__(self, project_path: Optional[Path] = None) -> None:
        """Initialize EnvWizard."""
        provided_path = project_path or Path.cwd()
        self.project_path = _validate_project_path(provided_path)
        logger.info(f"Initialized EnvWizard for project: {self.project_path}")
        self.project_detector = ProjectDetector(self.project_path)
        self.dependency_detector = DependencyDetector(self.project_path)
        self.venv_manager = VirtualEnvManager(self.project_path)
        self.dotenv_generator = DotEnvGenerator(self.project_path)

    def setup(
        self,
        venv_name: str = "venv",
        install_deps: bool = True,
        create_dotenv: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform complete environment setup.

        Args:
            venv_name: Name for virtual environment
            install_deps: Whether to install dependencies
            create_dotenv: Whether to create .env files

        Returns:
            Dictionary with setup results
        """
        results: Dict[str, Any] = {
            "project_info": {},
            "venv_created": False,
            "venv_path": None,
            "deps_installed": False,
            "dotenv_created": False,
            "errors": [],
            "messages": [],
        }

        # Detect project type
        project_info = self.project_detector.detect_project_type()
        results["project_info"] = project_info

        # Create virtual environment
        success, message, venv_path = self.venv_manager.create_venv(
            venv_name, project_info.get("python_version")
        )
        results["venv_created"] = success
        results["venv_path"] = str(venv_path) if venv_path else None
        results["messages"].append(message)

        if not success and "already exists" not in message:
            results["errors"].append(message)
            return results

        # Install dependencies
        if install_deps:
            dep_info = self.dependency_detector.get_dependency_file()
            if dep_info:
                _, dep_file = dep_info
                success, message = self.venv_manager.install_dependencies(venv_path, dep_file)
                results["deps_installed"] = success
                results["messages"].append(message)
                if not success:
                    results["errors"].append(message)
            else:
                results["messages"].append("No dependency file found, skipping installation")

        # Create .env files
        if create_dotenv:
            frameworks = project_info.get("frameworks", [])
            success, message = self.dotenv_generator.generate_dotenv(frameworks)
            results["dotenv_created"] = success
            results["messages"].append(message)

            if success:
                # Add .env to .gitignore
                success, message = self.dotenv_generator.add_to_gitignore()
                results["messages"].append(message)

        # Get activation command
        if results["venv_path"]:
            activation_cmd = self.venv_manager.get_activation_command(venv_path)
            results["activation_command"] = activation_cmd

        return results

    def get_project_info(self) -> Dict[str, Any]:
        """Get information about the current project."""
        return self.project_detector.detect_project_type()

    def create_venv_only(
        self, venv_name: str = "venv", python_version: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Path]]:
        """Create only the virtual environment."""
        return self.venv_manager.create_venv(venv_name, python_version)

    def create_dotenv_only(self, frameworks: Optional[list] = None) -> Tuple[bool, str]:
        """Create only .env files."""
        if frameworks is None:
            project_info = self.project_detector.detect_project_type()
            frameworks = project_info.get("frameworks", [])

        return self.dotenv_generator.generate_dotenv(frameworks)

    def install_dependencies_only(self, venv_path: Path) -> Tuple[bool, str]:
        """Install dependencies only."""
        dep_info = self.dependency_detector.get_dependency_file()
        if not dep_info:
            return False, "No dependency file found"

        _, dep_file = dep_info
        return self.venv_manager.install_dependencies(venv_path, dep_file)
