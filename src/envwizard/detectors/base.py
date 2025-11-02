"""Base project detector."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml


class ProjectDetector:
    """Detects project type and characteristics."""

    FRAMEWORK_INDICATORS = {
        "django": ["manage.py", "django", "settings.py"],
        "fastapi": ["fastapi", "main.py", "app.py"],
        "flask": ["flask", "app.py", "wsgi.py"],
        "streamlit": ["streamlit", ".streamlit"],
        "pandas": ["pandas", "data/", "notebooks/"],
        "numpy": ["numpy", "scientific"],
        "pytest": ["pytest", "tests/", "test_"],
        "requests": ["requests", "api/"],
        "sqlalchemy": ["sqlalchemy", "models.py", "database.py"],
        "celery": ["celery", "tasks.py", "celeryconfig.py"],
        "poetry": ["pyproject.toml", "poetry.lock"],
        "pipenv": ["Pipfile", "Pipfile.lock"],
    }

    def __init__(self, project_path: Optional[Path] = None) -> None:
        """Initialize detector with project path."""
        self.project_path = project_path or Path.cwd()
        self.detected_frameworks: Set[str] = set()
        self.detected_files: List[str] = []

    def detect_project_type(self) -> Dict[str, Any]:
        """Detect project type and return detailed information."""
        result = {
            "frameworks": [],
            "has_requirements": False,
            "has_pyproject": False,
            "has_setup_py": False,
            "has_pipfile": False,
            "python_version": None,
            "detected_files": [],
        }

        # Check for dependency files
        result["has_requirements"] = (self.project_path / "requirements.txt").exists()
        result["has_pyproject"] = (self.project_path / "pyproject.toml").exists()
        result["has_setup_py"] = (self.project_path / "setup.py").exists()
        result["has_pipfile"] = (self.project_path / "Pipfile").exists()

        # Detect frameworks
        frameworks = self._detect_frameworks()
        result["frameworks"] = list(frameworks)

        # Detect Python version from files
        result["python_version"] = self._detect_python_version()

        # Collect all relevant files
        result["detected_files"] = self._list_project_files()

        return result

    def _detect_frameworks(self) -> Set[str]:
        """Detect frameworks used in the project."""
        frameworks = set()

        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            frameworks.update(self._parse_requirements(req_file))

        # Check pyproject.toml
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            frameworks.update(self._parse_pyproject(pyproject_file))

        # Check Pipfile
        pipfile = self.project_path / "Pipfile"
        if pipfile.exists():
            frameworks.update(self._parse_pipfile(pipfile))

        # Check file structure
        frameworks.update(self._detect_from_structure())

        return frameworks

    def _parse_requirements(self, req_file: Path) -> Set[str]:
        """Parse requirements.txt for framework detection."""
        frameworks = set()
        try:
            content = req_file.read_text()
            for line in content.splitlines():
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue
                # Extract package name
                pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                for framework, indicators in self.FRAMEWORK_INDICATORS.items():
                    if pkg_name in [i.lower() for i in indicators]:
                        frameworks.add(framework)
        except Exception:
            pass
        return frameworks

    def _parse_pyproject(self, pyproject_file: Path) -> Set[str]:
        """Parse pyproject.toml for framework detection."""
        frameworks: Set[str] = set()
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                return frameworks

        try:
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)
                dependencies = []

                # Check various dependency locations
                if "project" in data and "dependencies" in data["project"]:
                    dependencies.extend(data["project"]["dependencies"])

                if "tool" in data and "poetry" in data["tool"]:
                    if "dependencies" in data["tool"]["poetry"]:
                        dependencies.extend(data["tool"]["poetry"]["dependencies"].keys())

                for dep in dependencies:
                    dep_name = dep.split("[")[0].split(">=")[0].split("==")[0].strip().lower()
                    for framework, indicators in self.FRAMEWORK_INDICATORS.items():
                        if dep_name in [i.lower() for i in indicators]:
                            frameworks.add(framework)
        except Exception:
            pass
        return frameworks

    def _parse_pipfile(self, pipfile: Path) -> Set[str]:
        """Parse Pipfile for framework detection."""
        frameworks = set()
        try:
            content = pipfile.read_text()
            # Simple parsing for packages section
            in_packages = False
            for line in content.splitlines():
                line = line.strip()
                if line == "[packages]":
                    in_packages = True
                    continue
                if line.startswith("[") and in_packages:
                    break
                if in_packages and "=" in line:
                    pkg_name = line.split("=")[0].strip().lower().strip('"').strip("'")
                    for framework, indicators in self.FRAMEWORK_INDICATORS.items():
                        if pkg_name in [i.lower() for i in indicators]:
                            frameworks.add(framework)
        except Exception:
            pass
        return frameworks

    def _detect_from_structure(self) -> Set[str]:
        """Detect frameworks from project file structure."""
        frameworks = set()

        for framework, indicators in self.FRAMEWORK_INDICATORS.items():
            for indicator in indicators:
                # Check for files
                if (self.project_path / indicator).exists():
                    frameworks.add(framework)
                    continue

                # Check for directories
                if (self.project_path / indicator).is_dir() if (self.project_path / indicator).exists() else False:
                    frameworks.add(framework)
                    continue

                # Check in subdirectories (first level only)
                for item in self.project_path.iterdir():
                    if item.is_dir():
                        if (item / indicator).exists():
                            frameworks.add(framework)
                            break

        return frameworks

    def _detect_python_version(self) -> Optional[str]:
        """Detect required Python version from project files."""
        # Check .python-version
        python_version_file = self.project_path / ".python-version"
        if python_version_file.exists():
            return python_version_file.read_text().strip()

        # Check runtime.txt (Heroku style)
        runtime_file = self.project_path / "runtime.txt"
        if runtime_file.exists():
            content = runtime_file.read_text().strip()
            if content.startswith("python-"):
                return content.replace("python-", "")

        # Check pyproject.toml
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib  # type: ignore
                except ImportError:
                    return None

            try:
                with open(pyproject_file, "rb") as f:
                    data = tomllib.load(f)
                    if "project" in data and "requires-python" in data["project"]:
                        requires_python = data["project"]["requires-python"]
                        return str(requires_python) if requires_python else None
            except Exception:
                pass

        return None

    def _list_project_files(self) -> List[str]:
        """List important project files."""
        important_files = []
        patterns = [
            "*.py",
            "requirements*.txt",
            "pyproject.toml",
            "setup.py",
            "Pipfile",
            "setup.cfg",
            ".python-version",
            "runtime.txt",
            "manage.py",
        ]

        for pattern in patterns:
            for file in self.project_path.glob(pattern):
                if file.is_file():
                    important_files.append(str(file.relative_to(self.project_path)))

        return important_files
