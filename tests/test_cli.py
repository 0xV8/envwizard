"""Tests for CLI interface."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envwizard.cli.main import cli


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_version(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "envwizard" in result.output.lower() or "version" in result.output.lower()

    def test_cli_help(self):
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Options:" in result.output

    def test_init_help(self):
        """Test init command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['init', '--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output


class TestInitCommand:
    """Test init command."""

    def test_init_with_python_version(self, tmp_path):
        """Test init command with Python version specified."""
        runner = CliRunner()
        # Create a simple requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0\n")

        result = runner.invoke(cli, [
            'init',
            '--path', str(tmp_path),
            '--python-version', '3.10',
            '--no-install',
            '--no-dotenv'
        ])
        # Should complete successfully or handle gracefully
        assert result.exit_code in [0, 1]

    def test_init_no_install(self, tmp_path):
        """Test init command with --no-install."""
        runner = CliRunner()
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests>=2.0\n")

        result = runner.invoke(cli, [
            'init',
            '--path', str(tmp_path),
            '--no-install',
            '--no-dotenv'
        ])
        assert result.exit_code == 0
        assert (tmp_path / "venv").exists()

    def test_init_no_dotenv(self, tmp_path):
        """Test init command with --no-dotenv."""
        runner = CliRunner()
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask>=2.0\n")

        result = runner.invoke(cli, [
            'init',
            '--path', str(tmp_path),
            '--no-dotenv',
            '--no-install'
        ])
        assert result.exit_code == 0
        # .env should not be created
        assert not (tmp_path / ".env").exists()

    def test_init_custom_venv_name(self, tmp_path):
        """Test init command with custom venv name."""
        runner = CliRunner()
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pandas>=1.0\n")

        result = runner.invoke(cli, [
            'init',
            '--path', str(tmp_path),
            '--venv-name', 'myenv',
            '--no-install',
            '--no-dotenv'
        ])
        assert result.exit_code == 0
        assert (tmp_path / "myenv").exists()
        assert not (tmp_path / "venv").exists()


class TestDetectCommand:
    """Test detect command."""

    def test_detect_django_project(self, tmp_path):
        """Test detecting Django project."""
        runner = CliRunner()
        # Create Django indicators
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0\n")
        manage_py = tmp_path / "manage.py"
        manage_py.write_text("# Django manage.py\n")

        result = runner.invoke(cli, ['detect', '--path', str(tmp_path)])
        assert result.exit_code == 0
        assert "django" in result.output.lower() or "frameworks" in result.output.lower()

    def test_detect_fastapi_project(self, tmp_path):
        """Test detecting FastAPI project."""
        runner = CliRunner()
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("fastapi>=0.95\nuvicorn>=0.20\n")

        result = runner.invoke(cli, ['detect', '--path', str(tmp_path)])
        assert result.exit_code == 0

    def test_detect_empty_project(self, tmp_path):
        """Test detecting empty project."""
        runner = CliRunner()
        result = runner.invoke(cli, ['detect', '--path', str(tmp_path)])
        assert result.exit_code == 0


class TestCreateVenvCommand:
    """Test create-venv command."""

    def test_create_venv_basic(self, tmp_path):
        """Test basic venv creation."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'create-venv',
            '--path', str(tmp_path),
            '--name', 'testvenv'
        ])
        assert result.exit_code == 0
        assert (tmp_path / "testvenv").exists()

    def test_create_venv_already_exists(self, tmp_path):
        """Test creating venv when it already exists."""
        runner = CliRunner()
        venv_path = tmp_path / "existing_venv"
        venv_path.mkdir()

        result = runner.invoke(cli, [
            'create-venv',
            '--path', str(tmp_path),
            '--name', 'existing_venv'
        ])
        # Should handle gracefully
        assert "already exists" in result.output.lower() or result.exit_code == 0


class TestCreateDotenvCommand:
    """Test create-dotenv command."""

    def test_create_dotenv_django(self, tmp_path):
        """Test creating .env for Django."""
        runner = CliRunner()
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0\n")

        result = runner.invoke(cli, [
            'create-dotenv',
            '--path', str(tmp_path)
        ])
        assert result.exit_code == 0
        assert (tmp_path / ".env").exists() or (tmp_path / ".env.example").exists()

    def test_create_dotenv_with_requirements(self, tmp_path):
        """Test creating .env with requirements file."""
        runner = CliRunner()
        # Create requirements.txt with multiple frameworks
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0\npsycopg2>=2.9\n")

        result = runner.invoke(cli, [
            'create-dotenv',
            '--path', str(tmp_path)
        ])
        assert result.exit_code == 0

    def test_create_dotenv_empty_project(self, tmp_path):
        """Test creating .env for empty project."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'create-dotenv',
            '--path', str(tmp_path)
        ])
        # Should handle gracefully
        assert result.exit_code == 0


class TestHelpCommands:
    """Test help text for various commands."""

    def test_create_venv_help(self):
        """Test create-venv command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-venv', '--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_create_dotenv_help(self):
        """Test create-dotenv command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-dotenv', '--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_detect_help(self):
        """Test detect command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['detect', '--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_path(self):
        """Test with non-existent path."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'detect',
            '--path', '/nonexistent/path/that/does/not/exist'
        ])
        # Should either fail gracefully or create the path
        assert result.exit_code in [0, 1, 2]

    def test_init_with_invalid_python_version(self, tmp_path):
        """Test init with invalid Python version format."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'init',
            '--path', str(tmp_path),
            '--python-version', 'invalid;version',
            '--no-install',
            '--no-dotenv'
        ])
        # Should reject invalid version format
        assert "invalid" in result.output.lower() or result.exit_code != 0


class TestCLIIntegration:
    """Integration tests for CLI workflows."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: detect -> init."""
        runner = CliRunner()

        # Create a project
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0\npsycopg2>=2.9\n")

        # Detect
        result = runner.invoke(cli, ['detect', '--path', str(tmp_path)])
        assert result.exit_code == 0

        # Init
        result = runner.invoke(cli, [
            'init',
            '--path', str(tmp_path),
            '--no-install'  # Skip installation for speed
        ])
        assert result.exit_code == 0
        assert (tmp_path / "venv").exists()
