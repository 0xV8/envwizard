"""Dependency detection and management."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class DependencyDetector:
    """Detect and manage project dependencies."""

    def __init__(self, project_path: Optional[Path] = None) -> None:
        """Initialize dependency detector."""
        self.project_path = project_path or Path.cwd()

    def get_dependency_file(self) -> Optional[Tuple[str, Path]]:
        """Determine which dependency file to use."""
        # Priority order
        files = [
            ("pyproject.toml", self.project_path / "pyproject.toml"),
            ("Pipfile", self.project_path / "Pipfile"),
            ("requirements.txt", self.project_path / "requirements.txt"),
            ("setup.py", self.project_path / "setup.py"),
        ]

        for file_type, file_path in files:
            if file_path.exists():
                return (file_type, file_path)

        return None

    def parse_requirements(self, req_file: Path) -> List[str]:
        """Parse requirements.txt and return list of packages."""
        packages = []
        try:
            content = req_file.read_text()
            for line in content.splitlines():
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Skip -e editable installs
                if line.startswith("-e"):
                    continue
                # Skip other pip options
                if line.startswith("-"):
                    continue
                packages.append(line)
        except Exception:
            pass
        return packages

    def get_all_dependencies(self) -> List[str]:
        """Get all project dependencies."""
        dep_info = self.get_dependency_file()
        if not dep_info:
            return []

        file_type, file_path = dep_info

        if file_type == "requirements.txt":
            return self.parse_requirements(file_path)
        elif file_type == "pyproject.toml":
            return self._parse_pyproject_deps(file_path)
        elif file_type == "Pipfile":
            return self._parse_pipfile_deps(file_path)

        return []

    def _parse_pyproject_deps(self, pyproject_file: Path) -> List[str]:
        """Parse dependencies from pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                return []

        try:
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)
                dependencies = []

                # Check project.dependencies
                if "project" in data and "dependencies" in data["project"]:
                    dependencies.extend(data["project"]["dependencies"])

                # Check tool.poetry.dependencies
                if "tool" in data and "poetry" in data["tool"]:
                    if "dependencies" in data["tool"]["poetry"]:
                        for dep, version in data["tool"]["poetry"]["dependencies"].items():
                            if dep != "python":
                                if isinstance(version, str):
                                    dependencies.append(f"{dep}{version}")
                                else:
                                    dependencies.append(dep)

                return dependencies
        except Exception:
            return []

    def _parse_pipfile_deps(self, pipfile: Path) -> List[str]:
        """Parse dependencies from Pipfile."""
        dependencies = []
        try:
            content = pipfile.read_text()
            in_packages = False

            for line in content.splitlines():
                line = line.strip()
                if line == "[packages]":
                    in_packages = True
                    continue
                if line.startswith("[") and in_packages:
                    break
                if in_packages and "=" in line:
                    pkg_name = line.split("=")[0].strip().strip('"').strip("'")
                    dependencies.append(pkg_name)
        except Exception:
            pass
        return dependencies

    def has_dev_dependencies(self) -> bool:
        """Check if project has dev dependencies defined."""
        dep_info = self.get_dependency_file()
        if not dep_info:
            return False

        file_type, file_path = dep_info

        if file_type == "requirements.txt":
            dev_req = self.project_path / "requirements-dev.txt"
            return dev_req.exists()
        elif file_type == "pyproject.toml":
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib  # type: ignore
                except ImportError:
                    return False

            try:
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
                    if "project" in data and "optional-dependencies" in data["project"]:
                        return "dev" in data["project"]["optional-dependencies"]
                    if "tool" in data and "poetry" in data["tool"]:
                        return "dev-dependencies" in data["tool"]["poetry"]
            except Exception:
                pass
        elif file_type == "Pipfile":
            content = file_path.read_text()
            return "[dev-packages]" in content

        return False
