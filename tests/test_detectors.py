"""Tests for detector modules."""

import pytest
from pathlib import Path

from envwizard.detectors import ProjectDetector, FrameworkDetector, DependencyDetector


class TestProjectDetector:
    """Tests for ProjectDetector."""

    def test_detect_django_project(self, django_project):
        """Test Django project detection."""
        detector = ProjectDetector(django_project)
        info = detector.detect_project_type()

        assert "django" in info["frameworks"]
        assert info["has_requirements"] is True
        assert "manage.py" in info["detected_files"]

    def test_detect_fastapi_project(self, fastapi_project):
        """Test FastAPI project detection."""
        detector = ProjectDetector(fastapi_project)
        info = detector.detect_project_type()

        assert "fastapi" in info["frameworks"]
        assert info["has_requirements"] is True
        assert "main.py" in info["detected_files"]

    def test_detect_flask_project(self, flask_project):
        """Test Flask project detection."""
        detector = ProjectDetector(flask_project)
        info = detector.detect_project_type()

        assert "flask" in info["frameworks"]
        assert info["has_requirements"] is True

    def test_detect_pyproject_toml(self, pyproject_project):
        """Test pyproject.toml detection."""
        detector = ProjectDetector(pyproject_project)
        info = detector.detect_project_type()

        assert info["has_pyproject"] is True
        assert "fastapi" in info["frameworks"]
        assert info["python_version"] == ">=3.8"

    def test_empty_project(self, empty_project):
        """Test empty project detection."""
        detector = ProjectDetector(empty_project)
        info = detector.detect_project_type()

        assert info["frameworks"] == []
        assert info["has_requirements"] is False
        assert info["has_pyproject"] is False


class TestFrameworkDetector:
    """Tests for FrameworkDetector."""

    def test_get_django_config(self):
        """Test Django framework configuration."""
        config = FrameworkDetector.get_framework_config("django")

        assert config is not None
        assert "env_vars" in config
        assert any(var[0] == "SECRET_KEY" for var in config["env_vars"])
        assert any(var[0] == "DEBUG" for var in config["env_vars"])

    def test_get_fastapi_config(self):
        """Test FastAPI framework configuration."""
        config = FrameworkDetector.get_framework_config("fastapi")

        assert config is not None
        assert "env_vars" in config
        assert any(var[0] == "API_V1_PREFIX" for var in config["env_vars"])

    def test_get_all_env_vars(self):
        """Test getting all environment variables for frameworks."""
        frameworks = ["django", "fastapi"]
        env_vars = FrameworkDetector.get_all_env_vars(frameworks)

        assert len(env_vars) > 0
        var_names = [var[0] for var in env_vars]
        assert "ENVIRONMENT" in var_names
        assert "LOG_LEVEL" in var_names

    def test_detect_postgresql(self, django_project):
        """Test PostgreSQL detection."""
        db_type = FrameworkDetector.detect_database(django_project)
        assert db_type == "postgresql"

    def test_get_database_env_vars(self):
        """Test database environment variables."""
        env_vars = FrameworkDetector.get_database_env_vars("postgresql")

        assert len(env_vars) > 0
        var_names = [var[0] for var in env_vars]
        assert "POSTGRES_HOST" in var_names
        assert "POSTGRES_PORT" in var_names


class TestDependencyDetector:
    """Tests for DependencyDetector."""

    def test_get_dependency_file_requirements(self, django_project):
        """Test finding requirements.txt."""
        detector = DependencyDetector(django_project)
        result = detector.get_dependency_file()

        assert result is not None
        file_type, file_path = result
        assert file_type == "requirements.txt"
        assert file_path.exists()

    def test_get_dependency_file_pyproject(self, pyproject_project):
        """Test finding pyproject.toml."""
        detector = DependencyDetector(pyproject_project)
        result = detector.get_dependency_file()

        assert result is not None
        file_type, file_path = result
        assert file_type == "pyproject.toml"
        assert file_path.exists()

    def test_parse_requirements(self, django_project):
        """Test parsing requirements.txt."""
        detector = DependencyDetector(django_project)
        req_file = django_project / "requirements.txt"
        packages = detector.parse_requirements(req_file)

        assert len(packages) > 0
        assert any("django" in pkg.lower() for pkg in packages)

    def test_get_all_dependencies(self, django_project):
        """Test getting all dependencies."""
        detector = DependencyDetector(django_project)
        deps = detector.get_all_dependencies()

        assert len(deps) > 0
        assert any("django" in dep.lower() for dep in deps)

    def test_empty_project_no_deps(self, empty_project):
        """Test empty project has no dependencies."""
        detector = DependencyDetector(empty_project)
        result = detector.get_dependency_file()

        assert result is None
