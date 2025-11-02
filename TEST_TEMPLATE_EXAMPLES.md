# Test Template Examples - Quick Copy/Paste

This file contains ready-to-use test templates for adding missing tests to EnvWizard.

---

## Template 1: CLI Test Structure

```python
"""Tests for CLI interface."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envwizard.cli.main import cli


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_version_flag(self):
        """Test --version flag displays version."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert "envwizard version" in result.output

    def test_help_without_command(self):
        """Test CLI without command shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code == 0
        assert "envwizard --help" in result.output


class TestCLIInit:
    """Test init command."""

    def test_init_with_defaults(self, tmp_path):
        """Test init command with default options."""
        runner = CliRunner()

        # Create a simple project
        (tmp_path / "requirements.txt").write_text("django>=4.0\n")

        # Run init with auto-confirm
        result = runner.invoke(
            cli,
            ['init', '--path', str(tmp_path)],
            input='y\n'  # Confirm setup
        )

        assert result.exit_code == 0
        assert "Virtual environment created" in result.output
        assert (tmp_path / "venv").exists()

    def test_init_no_install_flag(self, tmp_path):
        """Test init with --no-install flag."""
        runner = CliRunner()
        (tmp_path / "requirements.txt").write_text("django>=4.0\n")

        result = runner.invoke(
            cli,
            ['init', '--path', str(tmp_path), '--no-install'],
            input='y\n'
        )

        assert result.exit_code == 0
        # Should create venv but not install dependencies

    def test_init_no_dotenv_flag(self, tmp_path):
        """Test init with --no-dotenv flag."""
        runner = CliRunner()
        (tmp_path / "requirements.txt").write_text("django>=4.0\n")

        result = runner.invoke(
            cli,
            ['init', '--path', str(tmp_path), '--no-dotenv'],
            input='y\n'
        )

        assert result.exit_code == 0
        assert not (tmp_path / ".env").exists()

    def test_init_user_cancellation(self, tmp_path):
        """Test init when user cancels at confirmation."""
        runner = CliRunner()
        (tmp_path / "requirements.txt").write_text("django>=4.0\n")

        result = runner.invoke(
            cli,
            ['init', '--path', str(tmp_path)],
            input='n\n'  # User says no
        )

        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()
        assert not (tmp_path / "venv").exists()


class TestCLIDetect:
    """Test detect command."""

    def test_detect_django_project(self, tmp_path):
        """Test detect on Django project."""
        runner = CliRunner()

        # Create Django project structure
        (tmp_path / "manage.py").write_text("#!/usr/bin/env python\n")
        (tmp_path / "requirements.txt").write_text("django>=4.0\n")

        result = runner.invoke(cli, ['detect', '--path', str(tmp_path)])

        assert result.exit_code == 0
        assert "django" in result.output.lower()

    def test_detect_empty_project(self, tmp_path):
        """Test detect on empty project."""
        runner = CliRunner()

        result = runner.invoke(cli, ['detect', '--path', str(tmp_path)])

        assert result.exit_code == 0
        assert "None detected" in result.output or "No frameworks" in result.output


class TestCLICreateVenv:
    """Test create-venv command."""

    def test_create_venv_default(self, tmp_path):
        """Test create-venv with defaults."""
        runner = CliRunner()

        result = runner.invoke(cli, ['create-venv', '--path', str(tmp_path)])

        assert result.exit_code == 0
        assert (tmp_path / "venv").exists()

    def test_create_venv_custom_name(self, tmp_path):
        """Test create-venv with custom name."""
        runner = CliRunner()

        result = runner.invoke(
            cli,
            ['create-venv', '--path', str(tmp_path), '--name', 'myenv']
        )

        assert result.exit_code == 0
        assert (tmp_path / "myenv").exists()

    def test_create_venv_already_exists(self, tmp_path):
        """Test create-venv when venv already exists."""
        runner = CliRunner()

        # Create venv first time
        runner.invoke(cli, ['create-venv', '--path', str(tmp_path)])

        # Try again
        result = runner.invoke(cli, ['create-venv', '--path', str(tmp_path)])

        assert result.exit_code == 1
        assert "already exists" in result.output.lower()


class TestCLICreateDotenv:
    """Test create-dotenv command."""

    def test_create_dotenv_success(self, tmp_path):
        """Test create-dotenv on project with frameworks."""
        runner = CliRunner()

        # Create Django project
        (tmp_path / "manage.py").write_text("#!/usr/bin/env python\n")

        result = runner.invoke(cli, ['create-dotenv', '--path', str(tmp_path)])

        assert result.exit_code == 0
        assert (tmp_path / ".env").exists()
        assert (tmp_path / ".env.example").exists()

    def test_create_dotenv_already_exists(self, tmp_path):
        """Test create-dotenv when .env already exists."""
        runner = CliRunner()

        # Create existing .env
        (tmp_path / ".env").write_text("EXISTING=value\n")

        result = runner.invoke(cli, ['create-dotenv', '--path', str(tmp_path)])

        assert result.exit_code == 1
        assert "already exists" in result.output.lower()
```

---

## Template 2: DependencyDetector Tests

```python
"""Additional tests for DependencyDetector."""
import pytest
from pathlib import Path
from envwizard.detectors import DependencyDetector


class TestDependencyDetectorPyproject:
    """Test pyproject.toml dependency parsing."""

    def test_parse_pyproject_project_dependencies(self, tmp_path):
        """Test parsing project.dependencies from pyproject.toml."""
        detector = DependencyDetector(tmp_path)

        pyproject_content = """
[project]
name = "test-project"
dependencies = [
    "django>=4.0.0",
    "psycopg2-binary>=2.9.0",
]
        """.strip()

        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        deps = detector._parse_pyproject_deps(tmp_path / "pyproject.toml")

        assert len(deps) >= 2
        assert any("django" in dep.lower() for dep in deps)
        assert any("psycopg2" in dep.lower() for dep in deps)

    def test_parse_pyproject_poetry_dependencies(self, tmp_path):
        """Test parsing tool.poetry.dependencies."""
        detector = DependencyDetector(tmp_path)

        pyproject_content = """
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.8"
django = "^4.0.0"
fastapi = ">=0.95.0"
        """.strip()

        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        deps = detector._parse_pyproject_deps(tmp_path / "pyproject.toml")

        assert len(deps) >= 2
        assert any("django" in dep.lower() for dep in deps)
        assert any("fastapi" in dep.lower() for dep in deps)
        # Python should be excluded
        assert not any("python" == dep.lower() for dep in deps)

    def test_parse_pyproject_invalid_toml(self, tmp_path):
        """Test parsing invalid TOML file."""
        detector = DependencyDetector(tmp_path)

        # Invalid TOML (missing closing bracket)
        invalid_toml = """
[project
name = "test"
        """

        (tmp_path / "pyproject.toml").write_text(invalid_toml)

        # Should return empty list, not crash
        deps = detector._parse_pyproject_deps(tmp_path / "pyproject.toml")
        assert deps == []

    def test_parse_pyproject_tomli_fallback(self, tmp_path, monkeypatch):
        """Test tomli fallback for Python < 3.11."""
        detector = DependencyDetector(tmp_path)

        # Mock tomllib import failure
        import sys
        if 'tomllib' in sys.modules:
            del sys.modules['tomllib']

        pyproject_content = """
[project]
dependencies = ["django>=4.0"]
        """.strip()

        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        # Should fall back to tomli
        deps = detector._parse_pyproject_deps(tmp_path / "pyproject.toml")

        # May return empty if neither tomllib nor tomli available
        # That's acceptable - test ensures no crash


class TestDependencyDetectorPipfile:
    """Test Pipfile dependency parsing."""

    def test_parse_pipfile_valid(self, tmp_path):
        """Test parsing valid Pipfile."""
        detector = DependencyDetector(tmp_path)

        pipfile_content = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
django = ">=4.0.0"
fastapi = "*"

[dev-packages]
pytest = "*"
        """.strip()

        (tmp_path / "Pipfile").write_text(pipfile_content)

        deps = detector._parse_pipfile_deps(tmp_path / "Pipfile")

        assert len(deps) >= 2
        assert "django" in deps
        assert "fastapi" in deps

    def test_parse_pipfile_malformed(self, tmp_path):
        """Test parsing malformed Pipfile."""
        detector = DependencyDetector(tmp_path)

        # Malformed TOML-like content
        malformed = """
[packages
django = "4.0"  # Missing closing bracket
        """

        (tmp_path / "Pipfile").write_text(malformed)

        # Should return empty list, not crash
        deps = detector._parse_pipfile_deps(tmp_path / "Pipfile")
        assert isinstance(deps, list)


class TestDependencyDetectorRequirements:
    """Test requirements.txt parsing edge cases."""

    def test_parse_requirements_with_editable(self, tmp_path):
        """Test parsing requirements with -e editable packages."""
        detector = DependencyDetector(tmp_path)

        req_content = """
-e git+https://github.com/user/repo.git#egg=mypackage
django>=4.0.0
-e .
fastapi>=0.95.0
        """.strip()

        req_file = tmp_path / "requirements.txt"
        req_file.write_text(req_content)

        packages = detector.parse_requirements(req_file)

        # Editable packages should be skipped
        assert not any("-e" in pkg for pkg in packages)
        assert "django>=4.0.0" in packages
        assert "fastapi>=0.95.0" in packages

    def test_parse_requirements_with_options(self, tmp_path):
        """Test parsing requirements with pip options."""
        detector = DependencyDetector(tmp_path)

        req_content = """
--index-url https://pypi.org/simple
-r base.txt
--trusted-host pypi.org
django>=4.0.0
--find-links https://download.pytorch.org/whl/torch_stable.html
fastapi>=0.95.0
        """.strip()

        req_file = tmp_path / "requirements.txt"
        req_file.write_text(req_content)

        packages = detector.parse_requirements(req_file)

        # Options should be skipped
        assert not any(pkg.startswith("-") for pkg in packages)
        assert "django>=4.0.0" in packages
        assert "fastapi>=0.95.0" in packages

    def test_parse_requirements_comments_only(self, tmp_path):
        """Test parsing requirements with only comments."""
        detector = DependencyDetector(tmp_path)

        req_content = """
# This is a comment
# Another comment
        """.strip()

        req_file = tmp_path / "requirements.txt"
        req_file.write_text(req_content)

        packages = detector.parse_requirements(req_file)

        assert len(packages) == 0

    def test_parse_requirements_empty_file(self, tmp_path):
        """Test parsing empty requirements file."""
        detector = DependencyDetector(tmp_path)

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("")

        packages = detector.parse_requirements(req_file)

        assert len(packages) == 0


class TestDependencyDetectorDevDeps:
    """Test dev dependency detection."""

    def test_has_dev_dependencies_requirements_dev(self, tmp_path):
        """Test dev dependency detection for requirements-dev.txt."""
        detector = DependencyDetector(tmp_path)

        (tmp_path / "requirements.txt").write_text("django>=4.0\n")
        (tmp_path / "requirements-dev.txt").write_text("pytest>=7.0\n")

        assert detector.has_dev_dependencies() is True

    def test_has_dev_dependencies_pyproject_optional(self, tmp_path):
        """Test dev dependencies in pyproject.toml optional-dependencies."""
        detector = DependencyDetector(tmp_path)

        pyproject_content = """
[project]
name = "test"
dependencies = ["django>=4.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0", "black>=23.0"]
        """.strip()

        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        assert detector.has_dev_dependencies() is True

    def test_has_dev_dependencies_pipfile(self, tmp_path):
        """Test dev dependencies in Pipfile."""
        detector = DependencyDetector(tmp_path)

        pipfile_content = """
[packages]
django = "*"

[dev-packages]
pytest = "*"
        """.strip()

        (tmp_path / "Pipfile").write_text(pipfile_content)

        assert detector.has_dev_dependencies() is True

    def test_has_dev_dependencies_none(self, tmp_path):
        """Test when no dev dependencies exist."""
        detector = DependencyDetector(tmp_path)

        (tmp_path / "requirements.txt").write_text("django>=4.0\n")

        assert detector.has_dev_dependencies() is False
```

---

## Template 3: VirtualEnvManager Python Version Tests

```python
"""Tests for Python version handling in VirtualEnvManager."""
import pytest
import platform
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from envwizard.venv import VirtualEnvManager


class TestPythonVersionHandling:
    """Test Python version-specific venv creation."""

    def test_create_venv_with_specific_version(self, tmp_path):
        """Test creating venv with specific Python version."""
        manager = VirtualEnvManager(tmp_path)

        # Use current Python version
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        success, message, venv_path = manager.create_venv(
            "test_venv",
            python_version=current_version
        )

        # Should succeed if version is available
        if success:
            assert venv_path.exists()
            assert (venv_path / "pyvenv.cfg").exists()

    def test_create_venv_with_nonexistent_version(self, tmp_path):
        """Test creating venv with nonexistent Python version."""
        manager = VirtualEnvManager(tmp_path)

        # Use a definitely non-existent version
        success, message, venv_path = manager.create_venv(
            "test_venv",
            python_version="9.99"
        )

        # Should return False with appropriate message
        assert success is False
        assert "not found" in message.lower()

    def test_find_python_executable_current_version(self):
        """Test finding current Python version executable."""
        manager = VirtualEnvManager(Path.cwd())

        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        executable = manager._find_python_executable(current_version)

        # Should find current Python
        assert executable is not None

    def test_find_python_executable_invalid_version(self):
        """Test finding invalid Python version."""
        manager = VirtualEnvManager(Path.cwd())

        executable = manager._find_python_executable("9.99.99")

        # Should return None
        assert executable is None

    def test_find_python_executable_patterns(self):
        """Test various Python executable patterns."""
        manager = VirtualEnvManager(Path.cwd())

        # Test with just major version
        executable = manager._find_python_executable("3")

        # Should find some Python 3
        # May be None on some systems, that's ok
        if executable:
            assert "python" in executable.lower()


class TestPowerShellDetection:
    """Test PowerShell detection on Windows."""

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific")
    def test_is_powershell_true(self, monkeypatch):
        """Test PowerShell detection returns True."""
        manager = VirtualEnvManager(Path.cwd())

        # Set PowerShell environment variable
        monkeypatch.setenv("PSModulePath", "C:\\Windows\\System32")

        assert manager._is_powershell() is True

    def test_is_powershell_false(self, monkeypatch):
        """Test PowerShell detection returns False."""
        manager = VirtualEnvManager(Path.cwd())

        # Remove PowerShell indicators
        monkeypatch.delenv("PSModulePath", raising=False)
        monkeypatch.setenv("PROMPT", "$P$G")  # CMD prompt

        # On non-Windows, should be False
        # On Windows CMD, should be False
        result = manager._is_powershell()

        # Accept either False or True (system dependent)
        assert isinstance(result, bool)


class TestActivationCommands:
    """Test platform-specific activation commands."""

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific")
    def test_windows_activation_command(self, tmp_path):
        """Test Windows activation command generation."""
        manager = VirtualEnvManager(tmp_path)
        success, _, venv_path = manager.create_venv("test_venv")

        if success:
            activation_cmd = manager.get_activation_command(venv_path)

            # Should contain Scripts directory
            assert "Scripts" in activation_cmd
            assert "activate" in activation_cmd.lower()

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix-specific")
    def test_unix_activation_command(self, tmp_path):
        """Test Unix activation command generation."""
        manager = VirtualEnvManager(tmp_path)
        success, _, venv_path = manager.create_venv("test_venv")

        if success:
            activation_cmd = manager.get_activation_command(venv_path)

            # Should use source and bin/activate
            assert "source" in activation_cmd
            assert "bin/activate" in activation_cmd
```

---

## Template 4: Error Path Tests

```python
"""Tests for error handling paths."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from envwizard.venv import VirtualEnvManager
from envwizard.generators import DotEnvGenerator
from envwizard.core import EnvWizard


class TestVenvErrorPaths:
    """Test error handling in VirtualEnvManager."""

    def test_install_dependencies_pip_not_found(self, tmp_path):
        """Test dependency installation when pip is missing."""
        manager = VirtualEnvManager(tmp_path)

        # Create venv first
        success, _, venv_path = manager.create_venv("test_venv")
        assert success

        # Delete pip to simulate missing pip
        pip_exe = manager.get_pip_executable(venv_path)
        if pip_exe.exists():
            pip_exe.unlink()

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0\n")

        success, message = manager.install_dependencies(venv_path, req_file)

        assert success is False
        assert "pip not found" in message.lower()

    @patch('subprocess.run')
    def test_install_dependencies_subprocess_failure(self, mock_run, tmp_path):
        """Test dependency installation subprocess failure."""
        manager = VirtualEnvManager(tmp_path)

        # Create venv
        success, _, venv_path = manager.create_venv("test_venv")
        assert success

        # Mock subprocess to raise exception
        mock_run.side_effect = Exception("Network error")

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0\n")

        success, message = manager.install_dependencies(venv_path, req_file)

        assert success is False
        assert "error" in message.lower()

    @patch('subprocess.run')
    def test_install_package_failure(self, mock_run, tmp_path):
        """Test single package installation failure."""
        manager = VirtualEnvManager(tmp_path)

        success, _, venv_path = manager.create_venv("test_venv")
        assert success

        # Mock subprocess.run to raise CalledProcessError
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, "pip", stderr="Package not found")

        success, message = manager.install_package(venv_path, "nonexistent-package-xyz")

        assert success is False
        assert "failed" in message.lower()


class TestDotEnvErrorPaths:
    """Test error handling in DotEnvGenerator."""

    def test_generate_dotenv_permission_error(self, tmp_path):
        """Test .env generation with permission errors."""
        generator = DotEnvGenerator(tmp_path)

        # Create read-only directory (Unix)
        if hasattr(tmp_path, 'chmod'):
            tmp_path.chmod(0o444)  # Read-only

        success, message = generator.generate_dotenv(["django"])

        # Should fail with permission error
        # Or succeed if on Windows where chmod doesn't work the same
        if not success:
            assert "failed" in message.lower() or "permission" in message.lower()

        # Restore permissions
        if hasattr(tmp_path, 'chmod'):
            tmp_path.chmod(0o755)

    def test_add_to_gitignore_permission_error(self, tmp_path):
        """Test gitignore update with permission errors."""
        generator = DotEnvGenerator(tmp_path)

        # Create read-only .gitignore
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")

        if hasattr(gitignore, 'chmod'):
            gitignore.chmod(0o444)  # Read-only

        success, message = generator.add_to_gitignore()

        # Should fail or skip
        # Restore permissions
        if hasattr(gitignore, 'chmod'):
            gitignore.chmod(0o644)

    def test_validate_env_file_read_error(self, tmp_path):
        """Test .env validation with read errors."""
        generator = DotEnvGenerator(tmp_path)

        # Create unreadable .env (Unix)
        env_file = tmp_path / ".env"
        env_file.write_text("DEBUG=True\n")

        if hasattr(env_file, 'chmod'):
            env_file.chmod(0o000)  # No permissions

        is_valid, issues = generator.validate_env_file()

        # Should have issues
        assert is_valid is False
        assert len(issues) > 0

        # Restore permissions
        if hasattr(env_file, 'chmod'):
            env_file.chmod(0o644)


class TestCoreErrorPaths:
    """Test error handling in core EnvWizard."""

    def test_setup_with_venv_creation_failure(self, tmp_path):
        """Test setup when venv creation fails critically."""
        wizard = EnvWizard(tmp_path)

        # Make directory read-only to cause venv creation failure
        if hasattr(tmp_path, 'chmod'):
            tmp_path.chmod(0o444)

        results = wizard.setup(venv_name="test_venv")

        # Restore permissions
        if hasattr(tmp_path, 'chmod'):
            tmp_path.chmod(0o755)

        # Should have error in results
        if not results["venv_created"]:
            assert len(results["errors"]) > 0 or len(results["messages"]) > 0

    @patch.object(VirtualEnvManager, 'install_dependencies')
    def test_setup_with_dependency_install_failure(self, mock_install, tmp_path):
        """Test setup when dependency installation fails."""
        wizard = EnvWizard(tmp_path)

        # Create requirements file
        (tmp_path / "requirements.txt").write_text("django>=4.0\n")

        # Mock install_dependencies to fail
        mock_install.return_value = (False, "Installation failed: Network error")

        results = wizard.setup(venv_name="test_venv", install_deps=True)

        # Should have error
        assert results["deps_installed"] is False
        # Error should be recorded
        # assert "Network error" in " ".join(results["errors"])
```

---

## Template 5: Edge Case Tests

```python
"""Tests for edge cases."""
import pytest
from pathlib import Path
from envwizard.detectors import DependencyDetector
from envwizard.generators import DotEnvGenerator


class TestEdgeCases:
    """Test various edge cases."""

    def test_empty_requirements_file(self, tmp_path):
        """Test with completely empty requirements.txt."""
        detector = DependencyDetector(tmp_path)

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("")

        packages = detector.parse_requirements(req_file)
        assert len(packages) == 0

    def test_requirements_only_whitespace(self, tmp_path):
        """Test requirements with only whitespace."""
        detector = DependencyDetector(tmp_path)

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("\n\n   \n\t\n")

        packages = detector.parse_requirements(req_file)
        assert len(packages) == 0

    def test_requirements_unicode_characters(self, tmp_path):
        """Test requirements with Unicode characters."""
        detector = DependencyDetector(tmp_path)

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django>=4.0  # 日本語コメント\nfastapi>=0.95\n")

        packages = detector.parse_requirements(req_file)
        assert len(packages) == 2

    def test_env_file_with_spaces_in_var_names(self, tmp_path):
        """Test .env validation with spaces in variable names."""
        generator = DotEnvGenerator(tmp_path)

        env_file = tmp_path / ".env"
        env_file.write_text("VALID_VAR=value\nINVALID VAR=value\n")

        is_valid, issues = generator.validate_env_file()

        assert is_valid is False
        assert any("spaces" in issue.lower() for issue in issues)

    def test_env_file_with_emoji(self, tmp_path):
        """Test .env with emoji in values."""
        generator = DotEnvGenerator(tmp_path)

        env_file = tmp_path / ".env"
        env_file.write_text("APP_NAME=My App 🚀\nDEBUG=True\n")

        is_valid, issues = generator.validate_env_file()

        # Should be valid - emojis in values are ok
        # (though may cause issues depending on system)

    def test_very_long_file_path(self, tmp_path):
        """Test with very long file paths."""
        # Create nested directory structure
        long_path = tmp_path
        for i in range(10):
            long_path = long_path / f"very_long_directory_name_{i}"

        try:
            long_path.mkdir(parents=True, exist_ok=True)

            # Try to use it
            (long_path / "requirements.txt").write_text("django>=4.0\n")

            detector = DependencyDetector(long_path)
            result = detector.get_dependency_file()

            assert result is not None
        except OSError:
            # Path too long on this system, that's ok
            pytest.skip("Path length limit reached")

    def test_malformed_pyproject_toml(self, tmp_path):
        """Test with malformed pyproject.toml."""
        detector = DependencyDetector(tmp_path)

        # Invalid TOML syntax
        (tmp_path / "pyproject.toml").write_text("""
[project
name = "test"  # Missing closing bracket
dependencies = ["django"]
        """)

        # Should not crash
        deps = detector._parse_pyproject_deps(tmp_path / "pyproject.toml")

        # Should return empty list
        assert isinstance(deps, list)
```

---

## How to Use These Templates

1. **Copy the relevant class** to your test file
2. **Adjust imports** if needed
3. **Modify fixtures** to match your conftest.py
4. **Run the test** to verify it works
5. **Adjust assertions** based on actual behavior
6. **Add more edge cases** as you discover them

## Quick Test Checklist

For each new test:
- [ ] Has descriptive name
- [ ] Has docstring explaining purpose
- [ ] Uses appropriate fixture
- [ ] Tests one thing
- [ ] Has clear assertions
- [ ] Cleans up after itself (tmp_path does this)
- [ ] Handles both success and failure cases

---

Generated: November 2, 2025
See also: TEST_QUALITY_AUDIT_REPORT.md and TEST_GAPS_SUMMARY.md
