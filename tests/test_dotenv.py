"""Tests for .env file generation."""

import pytest
from pathlib import Path

from envwizard.generators import DotEnvGenerator


class TestDotEnvGenerator:
    """Tests for DotEnvGenerator."""

    def test_generate_dotenv_django(self, temp_project_dir):
        """Test .env generation for Django project."""
        generator = DotEnvGenerator(temp_project_dir)
        frameworks = ["django"]

        success, message = generator.generate_dotenv(frameworks)

        assert success is True
        assert (temp_project_dir / ".env").exists()
        assert (temp_project_dir / ".env.example").exists()

        # Check content
        env_content = (temp_project_dir / ".env").read_text()
        assert "SECRET_KEY" in env_content
        assert "DEBUG" in env_content
        assert "ALLOWED_HOSTS" in env_content

    def test_generate_dotenv_fastapi(self, temp_project_dir):
        """Test .env generation for FastAPI project."""
        generator = DotEnvGenerator(temp_project_dir)
        frameworks = ["fastapi"]

        success, message = generator.generate_dotenv(frameworks)

        assert success is True

        env_content = (temp_project_dir / ".env").read_text()
        assert "API_V1_PREFIX" in env_content
        assert "SECRET_KEY" in env_content

    def test_generate_dotenv_multiple_frameworks(self, temp_project_dir):
        """Test .env generation for multiple frameworks."""
        generator = DotEnvGenerator(temp_project_dir)
        frameworks = ["django", "celery"]

        success, message = generator.generate_dotenv(frameworks)

        assert success is True

        env_content = (temp_project_dir / ".env").read_text()
        assert "CELERY_BROKER_URL" in env_content
        assert "SECRET_KEY" in env_content

    def test_generate_dotenv_already_exists(self, temp_project_dir):
        """Test that existing .env is not overwritten."""
        generator = DotEnvGenerator(temp_project_dir)

        # Create existing .env
        (temp_project_dir / ".env").write_text("EXISTING=value\n")

        frameworks = ["django"]
        success, message = generator.generate_dotenv(frameworks)

        assert success is False
        assert "already exists" in message

        # Verify original content is preserved
        content = (temp_project_dir / ".env").read_text()
        assert "EXISTING=value" in content

    def test_env_example_has_placeholders(self, temp_project_dir):
        """Test that .env.example has placeholders for sensitive values."""
        generator = DotEnvGenerator(temp_project_dir)
        frameworks = ["django"]

        generator.generate_dotenv(frameworks)

        example_content = (temp_project_dir / ".env.example").read_text()
        # SECRET_KEY should have placeholder
        assert "<your-secret-key>" in example_content.lower()

    def test_add_to_gitignore_new_file(self, temp_project_dir):
        """Test adding .env to new .gitignore."""
        generator = DotEnvGenerator(temp_project_dir)

        success, message = generator.add_to_gitignore()

        assert success is True
        assert (temp_project_dir / ".gitignore").exists()

        gitignore_content = (temp_project_dir / ".gitignore").read_text()
        assert ".env" in gitignore_content

    def test_add_to_gitignore_existing_file(self, temp_project_dir):
        """Test adding .env to existing .gitignore."""
        generator = DotEnvGenerator(temp_project_dir)

        # Create existing .gitignore
        (temp_project_dir / ".gitignore").write_text("*.pyc\n__pycache__/\n")

        success, message = generator.add_to_gitignore()

        assert success is True

        gitignore_content = (temp_project_dir / ".gitignore").read_text()
        assert ".env" in gitignore_content
        assert "*.pyc" in gitignore_content  # Original content preserved

    def test_add_to_gitignore_already_present(self, temp_project_dir):
        """Test adding .env when already in .gitignore."""
        generator = DotEnvGenerator(temp_project_dir)

        # Create .gitignore with .env
        (temp_project_dir / ".gitignore").write_text(".env\n")

        success, message = generator.add_to_gitignore()

        assert success is True
        assert "already in" in message

    def test_validate_env_file(self, temp_project_dir):
        """Test .env file validation."""
        generator = DotEnvGenerator(temp_project_dir)

        # Create valid .env
        (temp_project_dir / ".env").write_text("DEBUG=True\nSECRET_KEY=mysecret\n")

        is_valid, issues = generator.validate_env_file()

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_env_file_with_issues(self, temp_project_dir):
        """Test validation of .env with issues."""
        generator = DotEnvGenerator(temp_project_dir)

        # Create .env with issues
        (temp_project_dir / ".env").write_text(
            "DEBUG=True\nSECRET_KEY=\nINVALID LINE\nAPI_KEY=<your-api-key>\n"
        )

        is_valid, issues = generator.validate_env_file()

        assert is_valid is False
        assert len(issues) > 0

    def test_validate_nonexistent_file(self, temp_project_dir):
        """Test validation of non-existent .env file."""
        generator = DotEnvGenerator(temp_project_dir)

        is_valid, issues = generator.validate_env_file()

        assert is_valid is False
        assert len(issues) > 0
        assert any("does not exist" in issue for issue in issues)

    def test_is_sensitive_variable(self, temp_project_dir):
        """Test sensitive variable detection."""
        generator = DotEnvGenerator(temp_project_dir)

        assert generator._is_sensitive("SECRET_KEY") is True
        assert generator._is_sensitive("PASSWORD") is True
        assert generator._is_sensitive("API_TOKEN") is True
        assert generator._is_sensitive("DEBUG") is False
        assert generator._is_sensitive("PORT") is False

    def test_section_name_detection(self, temp_project_dir):
        """Test section name detection for variables."""
        generator = DotEnvGenerator(temp_project_dir)

        assert "Database" in generator._get_section_name("POSTGRES_HOST")
        assert "Security" in generator._get_section_name("SECRET_KEY")
        assert "Task Queue" in generator._get_section_name("CELERY_BROKER_URL")
        assert "Application" in generator._get_section_name("DEBUG")
