"""Tests for core EnvWizard functionality."""

import pytest
from pathlib import Path

from envwizard.core import EnvWizard


class TestEnvWizard:
    """Tests for EnvWizard core functionality."""

    def test_initialization(self, temp_project_dir):
        """Test EnvWizard initialization."""
        wizard = EnvWizard(temp_project_dir)

        assert wizard.project_path == temp_project_dir
        assert wizard.project_detector is not None
        assert wizard.dependency_detector is not None
        assert wizard.venv_manager is not None
        assert wizard.dotenv_generator is not None

    def test_get_project_info(self, django_project):
        """Test getting project information."""
        wizard = EnvWizard(django_project)
        info = wizard.get_project_info()

        assert "frameworks" in info
        assert "django" in info["frameworks"]
        assert info["has_requirements"] is True

    def test_setup_django_project(self, django_project):
        """Test complete setup for Django project."""
        wizard = EnvWizard(django_project)
        results = wizard.setup(venv_name="test_venv", install_deps=False, create_dotenv=True)

        assert results["venv_created"] is True
        assert results["dotenv_created"] is True
        assert "activation_command" in results
        assert results["venv_path"] is not None

    def test_setup_skip_dotenv(self, django_project):
        """Test setup without creating .env files."""
        wizard = EnvWizard(django_project)
        results = wizard.setup(venv_name="test_venv", create_dotenv=False)

        assert results["venv_created"] is True
        assert results["dotenv_created"] is False

    def test_setup_skip_install(self, django_project):
        """Test setup without installing dependencies."""
        wizard = EnvWizard(django_project)
        results = wizard.setup(venv_name="test_venv", install_deps=False)

        assert results["venv_created"] is True
        # deps_installed should be False since we skipped installation

    def test_create_venv_only(self, temp_project_dir):
        """Test creating only virtual environment."""
        wizard = EnvWizard(temp_project_dir)
        success, message, venv_path = wizard.create_venv_only("my_venv")

        assert success is True
        assert venv_path.exists()
        assert venv_path.name == "my_venv"

    def test_create_dotenv_only(self, django_project):
        """Test creating only .env files."""
        wizard = EnvWizard(django_project)
        success, message = wizard.create_dotenv_only()

        assert success is True
        assert (django_project / ".env").exists()
        assert (django_project / ".env.example").exists()

    def test_create_dotenv_with_custom_frameworks(self, temp_project_dir):
        """Test creating .env with custom framework list."""
        wizard = EnvWizard(temp_project_dir)
        success, message = wizard.create_dotenv_only(frameworks=["fastapi", "celery"])

        assert success is True

        env_content = (temp_project_dir / ".env").read_text()
        assert "API_V1_PREFIX" in env_content
        assert "CELERY_BROKER_URL" in env_content

    def test_setup_empty_project(self, empty_project):
        """Test setup for empty project."""
        wizard = EnvWizard(empty_project)
        results = wizard.setup(venv_name="test_venv")

        # Should still create venv even if no frameworks detected
        assert results["venv_created"] is True
        # No dependencies to install
        assert results["deps_installed"] is False or "No dependency file" in str(
            results["messages"]
        )

    def test_setup_with_existing_venv(self, temp_project_dir):
        """Test setup when venv already exists."""
        wizard = EnvWizard(temp_project_dir)

        # Create venv first time
        wizard.create_venv_only("test_venv")

        # Try to setup again
        results = wizard.setup(venv_name="test_venv")

        assert results["venv_created"] is False
        assert any("already exists" in msg for msg in results["messages"])

    def test_install_dependencies_only_no_file(self, temp_project_dir):
        """Test installing dependencies when no file exists."""
        wizard = EnvWizard(temp_project_dir)

        # Create venv first
        _, _, venv_path = wizard.create_venv_only("test_venv")

        success, message = wizard.install_dependencies_only(venv_path)

        assert success is False
        assert "No dependency file" in message

    def test_install_dependencies_only_with_file(self, temp_project_dir):
        """Test installing dependencies from file."""
        wizard = EnvWizard(temp_project_dir)

        # Create requirements file
        (temp_project_dir / "requirements.txt").write_text("click>=8.0.0\n")

        # Create venv
        _, _, venv_path = wizard.create_venv_only("test_venv")

        success, message = wizard.install_dependencies_only(venv_path)

        assert success is True
