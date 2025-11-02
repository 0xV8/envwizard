"""Virtual environment creation and management."""

import os
import platform
import re
import subprocess
import sys
import venv
from pathlib import Path
from typing import Optional, Tuple

from envwizard.logger import get_logger

logger = get_logger(__name__)


def _validate_package_name(package: str) -> bool:
    """
    Validate package name to prevent command injection.

    Allows: alphanumeric, dots, hyphens, underscores, brackets, comparison operators
    Examples: django, numpy>=1.20.0, requests[security], pkg-name, my_package
    """
    # Pattern for valid pip package specifications
    # Covers: package-name, package[extras], package==1.0.0, package>=1.0,<2.0
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._\[\]>=<~!-]*$'
    return bool(re.match(pattern, package.strip()))


def _validate_python_version(version: str) -> bool:
    """
    Validate Python version string to prevent command injection.

    Allows: X.Y or X.Y.Z format (e.g., 3.9, 3.11.2)
    """
    pattern = r'^\d+(\.\d+)?(\.\d+)?$'
    return bool(re.match(pattern, version.strip()))


class VirtualEnvManager:
    """Manage virtual environment creation and activation."""

    def __init__(self, project_path: Optional[Path] = None) -> None:
        """Initialize virtual environment manager."""
        self.project_path = project_path or Path.cwd()
        self.system = platform.system()

    def create_venv(
        self, venv_name: str = "venv", python_version: Optional[str] = None
    ) -> Tuple[bool, str, Path]:
        """
        Create a virtual environment.

        Args:
            venv_name: Name of the virtual environment directory
            python_version: Specific Python version to use (optional)

        Returns:
            Tuple of (success, message, venv_path)
        """
        # Validate Python version to prevent command injection
        if python_version and not _validate_python_version(python_version):
            logger.warning(f"Invalid Python version format rejected: {python_version}")
            return False, f"Invalid Python version format: {python_version}. Expected format: X.Y or X.Y.Z (e.g., 3.9, 3.11.2)", Path()

        venv_path = self.project_path / venv_name

        if venv_path.exists():
            logger.debug(f"Virtual environment already exists: {venv_path}")
            return False, f"Virtual environment '{venv_name}' already exists", venv_path

        logger.info(f"Creating virtual environment: {venv_path}")
        try:
            # If specific Python version requested, try to use it
            if python_version:
                python_executable = self._find_python_executable(python_version)
                if python_executable:
                    subprocess.run(
                        [python_executable, "-m", "venv", str(venv_path)],
                        check=True,
                        capture_output=True,
                    )
                else:
                    return (
                        False,
                        f"Python {python_version} not found. Using system default.",
                        venv_path,
                    )
            else:
                # Use standard library venv
                venv.create(venv_path, with_pip=True, clear=False)

            return True, f"Virtual environment created at {venv_path}", venv_path

        except Exception as e:
            return False, f"Failed to create virtual environment: {str(e)}", venv_path

    def get_activation_command(self, venv_path: Path) -> str:
        """Get the command to activate the virtual environment."""
        if self.system == "Windows":
            if self._is_powershell():
                return str(venv_path / "Scripts" / "Activate.ps1")
            else:
                return str(venv_path / "Scripts" / "activate.bat")
        else:
            return f"source {venv_path}/bin/activate"

    def get_python_executable(self, venv_path: Path) -> Path:
        """Get the Python executable path in the virtual environment."""
        if self.system == "Windows":
            return venv_path / "Scripts" / "python.exe"
        else:
            return venv_path / "bin" / "python"

    def get_pip_executable(self, venv_path: Path) -> Path:
        """Get the pip executable path in the virtual environment."""
        if self.system == "Windows":
            return venv_path / "Scripts" / "pip.exe"
        else:
            return venv_path / "bin" / "pip"

    def install_dependencies(
        self, venv_path: Path, requirements_file: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """
        Install dependencies in the virtual environment.

        Args:
            venv_path: Path to virtual environment
            requirements_file: Path to requirements file (optional)

        Returns:
            Tuple of (success, message)
        """
        pip_exe = self.get_pip_executable(venv_path)

        if not pip_exe.exists():
            return False, "pip not found in virtual environment"

        try:
            # Upgrade pip first
            subprocess.run(
                [str(pip_exe), "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                text=True,
            )

            if requirements_file and requirements_file.exists():
                # Install from requirements file
                result = subprocess.run(
                    [str(pip_exe), "install", "-r", str(requirements_file)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    return True, "Dependencies installed successfully"
                else:
                    return False, f"Failed to install dependencies: {result.stderr}"
            else:
                return True, "No requirements file found, skipping dependency installation"

        except subprocess.CalledProcessError as e:
            return False, f"Failed to install dependencies: {str(e)}"
        except Exception as e:
            return False, f"Error during installation: {str(e)}"

    def install_package(self, venv_path: Path, package: str) -> Tuple[bool, str]:
        """Install a single package in the virtual environment."""
        # Validate package name to prevent command injection
        if not _validate_package_name(package):
            logger.warning(f"Invalid package name rejected: {package}")
            return False, f"Invalid package name: {package}. Package names must be alphanumeric with allowed characters: ._[]>=<~!-"

        logger.info(f"Installing package: {package}")

        pip_exe = self.get_pip_executable(venv_path)

        if not pip_exe.exists():
            return False, "pip not found in virtual environment"

        try:
            result = subprocess.run(
                [str(pip_exe), "install", package],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Package '{package}' installed successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install {package}: {e.stderr}"

    def _find_python_executable(self, version: str) -> Optional[str]:
        """Find Python executable for a specific version."""
        # Common patterns to try
        patterns = [
            f"python{version}",
            f"python{version.split('.')[0]}.{version.split('.')[1]}",
            f"python{version.split('.')[0]}",
            "python3",
            "python",
        ]

        for pattern in patterns:
            try:
                result = subprocess.run(
                    [pattern, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return pattern
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return None

    def _is_powershell(self) -> bool:
        """Check if running in PowerShell."""
        return "POWERSHELL" in os.environ.get("PROMPT", "").upper() or os.environ.get(
            "PSModulePath"
        ) is not None

    def get_venv_info(self, venv_path: Path) -> dict:
        """Get information about an existing virtual environment."""
        if not venv_path.exists():
            return {"exists": False}

        python_exe = self.get_python_executable(venv_path)
        info = {
            "exists": True,
            "path": str(venv_path),
            "python_executable": str(python_exe),
            "activation_command": self.get_activation_command(venv_path),
        }

        # Try to get Python version
        if python_exe.exists():
            try:
                result = subprocess.run(
                    [str(python_exe), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    info["python_version"] = result.stdout.strip()
            except Exception:
                pass

        return info
