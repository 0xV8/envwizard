#!/usr/bin/env python3
"""
Real-World Testing Suite for envwizard

This script performs comprehensive end-to-end testing of envwizard
on actual Python projects to verify production readiness.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestResult:
    """Store test result information."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.details: Dict[str, Any] = {}
        self.execution_time = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
            "execution_time": self.execution_time
        }


class EnvWizardRealWorldTester:
    """Real-world testing suite for envwizard."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.test_results: List[TestResult] = []
        self.start_time = datetime.now()

    def print_header(self, text: str):
        """Print formatted header."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

    def print_test_start(self, test_name: str):
        """Print test start message."""
        print(f"{Colors.OKCYAN}{Colors.BOLD}► Testing: {test_name}{Colors.ENDC}")

    def print_success(self, message: str):
        """Print success message."""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

    def print_error(self, message: str):
        """Print error message."""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

    def print_warning(self, message: str):
        """Print warning message."""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

    def run_command(self, cmd: List[str], cwd: Path, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run shell command and return result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 5 minutes"
        except Exception as e:
            return -1, "", str(e)

    def cleanup_test_dir(self, test_dir: Path):
        """Clean up test directory."""
        if test_dir.exists():
            shutil.rmtree(test_dir)
        test_dir.mkdir(parents=True, exist_ok=True)

    def verify_file_exists(self, file_path: Path, result: TestResult) -> bool:
        """Verify a file exists."""
        if not file_path.exists():
            result.errors.append(f"Expected file not found: {file_path}")
            return False
        self.print_success(f"File exists: {file_path.name}")
        return True

    def verify_venv_activation(self, venv_path: Path, result: TestResult) -> bool:
        """Verify virtual environment can be activated."""
        if sys.platform == "win32":
            activate_script = venv_path / "Scripts" / "activate.bat"
        else:
            activate_script = venv_path / "bin" / "activate"

        if not activate_script.exists():
            result.errors.append(f"Activation script not found: {activate_script}")
            return False

        self.print_success("Virtual environment activation script exists")
        return True

    def verify_dotenv_format(self, dotenv_path: Path, result: TestResult) -> bool:
        """Verify .env file has correct format."""
        if not dotenv_path.exists():
            result.errors.append(".env file not found")
            return False

        content = dotenv_path.read_text()

        # Check for basic structure
        checks = {
            "Has comments": "#" in content,
            "Has key=value pairs": "=" in content,
            "Non-empty": len(content.strip()) > 0
        }

        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                self.print_success(f".env format: {check_name}")
            else:
                self.print_error(f".env format: {check_name} - FAILED")
                result.errors.append(f".env format check failed: {check_name}")
                all_passed = False

        result.details["dotenv_lines"] = len(content.splitlines())
        result.details["dotenv_size"] = len(content)

        return all_passed

    def test_django_project(self) -> TestResult:
        """Test envwizard on a Django project."""
        result = TestResult("Django Project")
        self.print_test_start(result.test_name)

        test_dir = self.base_dir / "test_django"
        self.cleanup_test_dir(test_dir)

        try:
            # Create Django project structure
            (test_dir / "manage.py").write_text("""#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
""")

            (test_dir / "myproject").mkdir()
            (test_dir / "myproject" / "__init__.py").touch()
            (test_dir / "myproject" / "settings.py").write_text("""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'test-key'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
""")

            (test_dir / "myproject" / "urls.py").write_text("""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
""")

            (test_dir / "requirements.txt").write_text("""Django>=4.2.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
""")

            # Run envwizard init
            self.print_success("Django project structure created")

            returncode, stdout, stderr = self.run_command(
                ["envwizard", "init", "--path", str(test_dir), "--venv-name", "venv"],
                cwd=test_dir
            )

            result.details["envwizard_returncode"] = returncode
            result.details["envwizard_stdout"] = stdout
            result.details["envwizard_stderr"] = stderr

            if returncode != 0:
                result.errors.append(f"envwizard init failed with code {returncode}")
                result.errors.append(f"stderr: {stderr}")
                return result

            self.print_success("envwizard init completed successfully")

            # Verify outputs
            venv_path = test_dir / "venv"
            dotenv_path = test_dir / ".env"
            dotenv_example = test_dir / ".env.example"

            checks = [
                self.verify_file_exists(venv_path, result),
                self.verify_file_exists(dotenv_path, result),
                self.verify_file_exists(dotenv_example, result),
                self.verify_venv_activation(venv_path, result),
                self.verify_dotenv_format(dotenv_path, result)
            ]

            # Check .env content for Django-specific vars
            dotenv_content = dotenv_path.read_text()
            django_vars = ["SECRET_KEY", "DEBUG", "ALLOWED_HOSTS"]
            for var in django_vars:
                if var in dotenv_content:
                    self.print_success(f".env contains Django variable: {var}")
                else:
                    self.print_warning(f".env missing Django variable: {var}")
                    result.warnings.append(f"Missing Django variable: {var}")

            # Check for database configuration
            if "DATABASE_URL" in dotenv_content or "POSTGRES" in dotenv_content:
                self.print_success(".env contains database configuration")
            else:
                self.print_warning(".env missing database configuration")
                result.warnings.append("Missing database configuration")

            result.passed = all(checks) and len(result.errors) == 0

        except Exception as e:
            result.errors.append(f"Exception during test: {str(e)}")
            import traceback
            result.details["traceback"] = traceback.format_exc()

        return result

    def test_fastapi_project(self) -> TestResult:
        """Test envwizard on a FastAPI project."""
        result = TestResult("FastAPI Project")
        self.print_test_start(result.test_name)

        test_dir = self.base_dir / "test_fastapi"
        self.cleanup_test_dir(test_dir)

        try:
            # Create FastAPI project structure
            (test_dir / "main.py").write_text("""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
""")

            (test_dir / "requirements.txt").write_text("""fastapi>=0.100.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0
python-dotenv>=1.0.0
redis>=4.5.0
""")

            (test_dir / "config.py").write_text("""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    redis_url: str = "redis://localhost:6379"
    api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
""")

            self.print_success("FastAPI project structure created")

            # Run envwizard init
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "init", "--path", str(test_dir)],
                cwd=test_dir
            )

            result.details["envwizard_returncode"] = returncode
            result.details["envwizard_stdout"] = stdout
            result.details["envwizard_stderr"] = stderr

            if returncode != 0:
                result.errors.append(f"envwizard init failed with code {returncode}")
                result.errors.append(f"stderr: {stderr}")
                return result

            self.print_success("envwizard init completed successfully")

            # Verify outputs
            venv_path = test_dir / "venv"
            dotenv_path = test_dir / ".env"

            checks = [
                self.verify_file_exists(venv_path, result),
                self.verify_file_exists(dotenv_path, result),
                self.verify_venv_activation(venv_path, result),
                self.verify_dotenv_format(dotenv_path, result)
            ]

            # Check .env content for FastAPI-specific vars
            dotenv_content = dotenv_path.read_text()
            fastapi_indicators = ["API", "HOST", "PORT"]
            found_indicators = [ind for ind in fastapi_indicators if ind in dotenv_content]

            if found_indicators:
                self.print_success(f".env contains API-related variables: {', '.join(found_indicators)}")

            # Check for Redis configuration (detected from requirements)
            if "REDIS" in dotenv_content:
                self.print_success(".env contains Redis configuration")
            else:
                self.print_warning(".env missing Redis configuration")
                result.warnings.append("Missing Redis configuration")

            result.passed = all(checks) and len(result.errors) == 0

        except Exception as e:
            result.errors.append(f"Exception during test: {str(e)}")
            import traceback
            result.details["traceback"] = traceback.format_exc()

        return result

    def test_empty_project(self) -> TestResult:
        """Test envwizard on an empty project."""
        result = TestResult("Empty Project")
        self.print_test_start(result.test_name)

        test_dir = self.base_dir / "test_empty"
        self.cleanup_test_dir(test_dir)

        try:
            # Create minimal project with just a Python file
            (test_dir / "app.py").write_text("""
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
""")

            self.print_success("Empty project created")

            # Run envwizard detect
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "detect", "--path", str(test_dir)],
                cwd=test_dir
            )

            result.details["detect_returncode"] = returncode
            result.details["detect_stdout"] = stdout

            if returncode == 0:
                self.print_success("envwizard detect handled empty project gracefully")
            else:
                result.errors.append(f"envwizard detect failed on empty project: {stderr}")

            # Try create-dotenv on empty project
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "create-dotenv", "--path", str(test_dir)],
                cwd=test_dir
            )

            if returncode == 0:
                self.print_success("envwizard create-dotenv handled empty project")
                dotenv_path = test_dir / ".env"
                if dotenv_path.exists():
                    self.print_success("Generic .env file created for empty project")
                    result.details["dotenv_created"] = True

            result.passed = len(result.errors) == 0

        except Exception as e:
            result.errors.append(f"Exception during test: {str(e)}")
            import traceback
            result.details["traceback"] = traceback.format_exc()

        return result

    def test_multiple_frameworks(self) -> TestResult:
        """Test envwizard on a project with multiple frameworks."""
        result = TestResult("Multiple Frameworks Project")
        self.print_test_start(result.test_name)

        test_dir = self.base_dir / "test_multi_framework"
        self.cleanup_test_dir(test_dir)

        try:
            # Create project with Django + Celery + Redis + PostgreSQL
            (test_dir / "manage.py").write_text("""#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
""")

            (test_dir / "celery_app.py").write_text("""
from celery import Celery

app = Celery('myapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
""")

            (test_dir / "requirements.txt").write_text("""Django>=4.2.0
celery>=5.3.0
redis>=4.5.0
psycopg2-binary>=2.9.0
django-celery-beat>=2.5.0
python-dotenv>=1.0.0
pytest>=7.0.0
""")

            self.print_success("Multi-framework project structure created")

            # Run envwizard init
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "init", "--path", str(test_dir)],
                cwd=test_dir
            )

            result.details["envwizard_returncode"] = returncode

            if returncode != 0:
                result.errors.append(f"envwizard init failed: {stderr}")
                return result

            self.print_success("envwizard init completed")

            # Verify all frameworks detected
            dotenv_path = test_dir / ".env"
            if dotenv_path.exists():
                dotenv_content = dotenv_path.read_text()

                expected_frameworks = {
                    "Django": ["DJANGO", "SECRET_KEY", "DEBUG"],
                    "Celery": ["CELERY"],
                    "Redis": ["REDIS"],
                    "PostgreSQL": ["POSTGRES", "DATABASE"]
                }

                detected_frameworks = []
                for framework, indicators in expected_frameworks.items():
                    if any(ind in dotenv_content for ind in indicators):
                        detected_frameworks.append(framework)
                        self.print_success(f"Detected {framework} configuration in .env")
                    else:
                        self.print_warning(f"{framework} configuration not found in .env")
                        result.warnings.append(f"Missing {framework} configuration")

                result.details["detected_frameworks"] = detected_frameworks
                result.details["expected_frameworks"] = list(expected_frameworks.keys())

                if len(detected_frameworks) >= 2:
                    self.print_success(f"Multiple frameworks detected: {', '.join(detected_frameworks)}")
                    result.passed = True
                else:
                    result.errors.append("Expected multiple frameworks to be detected")
            else:
                result.errors.append(".env file not created")

        except Exception as e:
            result.errors.append(f"Exception during test: {str(e)}")
            import traceback
            result.details["traceback"] = traceback.format_exc()

        return result

    def test_complex_dependencies(self) -> TestResult:
        """Test envwizard with complex dependency scenarios."""
        result = TestResult("Complex Dependencies")
        self.print_test_start(result.test_name)

        test_dir = self.base_dir / "test_complex_deps"
        self.cleanup_test_dir(test_dir)

        try:
            # Create project with various dependency formats
            (test_dir / "requirements.txt").write_text("""# Web framework
Flask==2.3.0
flask-cors>=1.10.0

# Database
SQLAlchemy>=2.0.0
alembic~=1.11.0

# Data processing
pandas>=2.0.0,<3.0.0
numpy>=1.24.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Development
black==23.7.0
ruff>=0.0.280

# Conditional dependencies
psycopg2-binary>=2.9.0; sys_platform != 'win32'

# Git dependencies (comment)
# -e git+https://github.com/example/package.git@main#egg=package
""")

            (test_dir / "app.py").write_text("""
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'
""")

            self.print_success("Complex dependencies project created")

            # Run envwizard init without installing (to save time)
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "init", "--path", str(test_dir), "--no-install"],
                cwd=test_dir
            )

            result.details["envwizard_returncode"] = returncode

            if returncode != 0:
                result.errors.append(f"envwizard init failed: {stderr}")
                return result

            self.print_success("envwizard handled complex dependencies")

            # Verify venv and .env created
            venv_path = test_dir / "venv"
            dotenv_path = test_dir / ".env"

            checks = [
                self.verify_file_exists(venv_path, result),
                self.verify_file_exists(dotenv_path, result)
            ]

            # Check if Flask was detected
            dotenv_content = dotenv_path.read_text()
            if "FLASK" in dotenv_content or "APP" in dotenv_content:
                self.print_success("Flask configuration detected")

            result.passed = all(checks) and len(result.errors) == 0

        except Exception as e:
            result.errors.append(f"Exception during test: {str(e)}")
            import traceback
            result.details["traceback"] = traceback.format_exc()

        return result

    def test_existing_venv(self) -> TestResult:
        """Test envwizard with an existing virtual environment."""
        result = TestResult("Existing Virtual Environment")
        self.print_test_start(result.test_name)

        test_dir = self.base_dir / "test_existing_venv"
        self.cleanup_test_dir(test_dir)

        try:
            # Create a simple project
            (test_dir / "app.py").write_text("print('Hello')")
            (test_dir / "requirements.txt").write_text("requests>=2.31.0\n")

            # Create venv manually first
            returncode, stdout, stderr = self.run_command(
                [sys.executable, "-m", "venv", "venv"],
                cwd=test_dir
            )

            if returncode != 0:
                result.errors.append(f"Failed to create initial venv: {stderr}")
                return result

            self.print_success("Pre-existing virtual environment created")

            # Run envwizard init (should handle existing venv gracefully)
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "init", "--path", str(test_dir), "--no-install"],
                cwd=test_dir
            )

            result.details["envwizard_returncode"] = returncode
            result.details["envwizard_stdout"] = stdout
            result.details["envwizard_stderr"] = stderr

            # Should not fail - either skip or reuse existing venv
            if returncode == 0:
                self.print_success("envwizard handled existing venv gracefully")
                result.passed = True
            else:
                # Check if error message is informative
                if "already exists" in stderr.lower() or "already exists" in stdout.lower():
                    self.print_success("envwizard detected existing venv with clear message")
                    result.passed = True
                else:
                    result.errors.append("envwizard failed to handle existing venv properly")

        except Exception as e:
            result.errors.append(f"Exception during test: {str(e)}")
            import traceback
            result.details["traceback"] = traceback.format_exc()

        return result

    def test_cli_commands(self) -> TestResult:
        """Test all CLI commands in real scenarios."""
        result = TestResult("CLI Commands")
        self.print_test_start(result.test_name)

        test_dir = self.base_dir / "test_cli"
        self.cleanup_test_dir(test_dir)

        try:
            # Setup basic project
            (test_dir / "app.py").write_text("print('test')")
            (test_dir / "requirements.txt").write_text("requests>=2.31.0\n")

            # Test 1: envwizard detect
            self.print_success("Testing: envwizard detect")
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "detect", "--path", str(test_dir)],
                cwd=test_dir
            )

            if returncode == 0:
                self.print_success("envwizard detect: PASSED")
                result.details["detect_passed"] = True
            else:
                result.errors.append(f"envwizard detect failed: {stderr}")
                result.details["detect_passed"] = False

            # Test 2: envwizard create-venv
            self.print_success("Testing: envwizard create-venv")
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "create-venv", "--path", str(test_dir), "--name", "test_venv"],
                cwd=test_dir
            )

            if returncode == 0 and (test_dir / "test_venv").exists():
                self.print_success("envwizard create-venv: PASSED")
                result.details["create_venv_passed"] = True
            else:
                result.errors.append(f"envwizard create-venv failed: {stderr}")
                result.details["create_venv_passed"] = False

            # Test 3: envwizard create-dotenv
            self.print_success("Testing: envwizard create-dotenv")
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "create-dotenv", "--path", str(test_dir)],
                cwd=test_dir
            )

            if returncode == 0 and (test_dir / ".env").exists():
                self.print_success("envwizard create-dotenv: PASSED")
                result.details["create_dotenv_passed"] = True
            else:
                result.errors.append(f"envwizard create-dotenv failed: {stderr}")
                result.details["create_dotenv_passed"] = False

            # Test 4: envwizard --version
            self.print_success("Testing: envwizard --version")
            returncode, stdout, stderr = self.run_command(
                ["envwizard", "--version"],
                cwd=test_dir
            )

            if returncode == 0 and "version" in stdout.lower():
                self.print_success("envwizard --version: PASSED")
                result.details["version_passed"] = True
                result.details["version_output"] = stdout.strip()
            else:
                result.errors.append("envwizard --version failed")
                result.details["version_passed"] = False

            # All tests must pass
            all_tests_passed = all([
                result.details.get("detect_passed", False),
                result.details.get("create_venv_passed", False),
                result.details.get("create_dotenv_passed", False),
                result.details.get("version_passed", False)
            ])

            result.passed = all_tests_passed and len(result.errors) == 0

        except Exception as e:
            result.errors.append(f"Exception during test: {str(e)}")
            import traceback
            result.details["traceback"] = traceback.format_exc()

        return result

    def run_all_tests(self) -> List[TestResult]:
        """Run all real-world tests."""
        self.print_header("ENVWIZARD REAL-WORLD TESTING SUITE")

        tests = [
            self.test_django_project,
            self.test_fastapi_project,
            self.test_empty_project,
            self.test_multiple_frameworks,
            self.test_complex_dependencies,
            self.test_existing_venv,
            self.test_cli_commands
        ]

        for test_func in tests:
            start = datetime.now()
            result = test_func()
            result.execution_time = (datetime.now() - start).total_seconds()
            self.test_results.append(result)

            if result.passed:
                self.print_success(f"✓ {result.test_name} PASSED ({result.execution_time:.2f}s)")
            else:
                self.print_error(f"✗ {result.test_name} FAILED ({result.execution_time:.2f}s)")

            print()

        return self.test_results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests

        total_errors = sum(len(r.errors) for r in self.test_results)
        total_warnings = sum(len(r.warnings) for r in self.test_results)

        total_time = (datetime.now() - self.start_time).total_seconds()

        # Calculate production readiness score
        score_components = {
            "test_pass_rate": (passed_tests / total_tests * 100) * 0.4,  # 40%
            "error_penalty": max(0, 100 - (total_errors * 10)) * 0.3,    # 30%
            "warning_penalty": max(0, 100 - (total_warnings * 5)) * 0.2, # 20%
            "performance": min(100, (1 / (total_time / total_tests)) * 10) * 0.1  # 10%
        }

        production_readiness_score = sum(score_components.values())

        # Determine readiness level
        if production_readiness_score >= 90:
            readiness_level = "Production Ready"
        elif production_readiness_score >= 75:
            readiness_level = "Nearly Production Ready"
        elif production_readiness_score >= 60:
            readiness_level = "Beta Quality"
        else:
            readiness_level = "Not Production Ready"

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "total_execution_time": total_time,
                "production_readiness_score": round(production_readiness_score, 2),
                "readiness_level": readiness_level
            },
            "test_results": [r.to_dict() for r in self.test_results],
            "bugs_found": [],
            "recommendations": []
        }

        # Collect bugs from failed tests
        for result in self.test_results:
            if not result.passed or result.errors:
                for error in result.errors:
                    report["bugs_found"].append({
                        "test": result.test_name,
                        "error": error,
                        "severity": "high" if not result.passed else "medium"
                    })

        # Generate recommendations
        if failed_tests > 0:
            report["recommendations"].append(
                "Fix failing tests before production deployment"
            )

        if total_warnings > 5:
            report["recommendations"].append(
                "Address warnings to improve user experience and completeness"
            )

        if production_readiness_score < 75:
            report["recommendations"].append(
                "Significant improvements needed before production use"
            )

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report."""
        self.print_header("TEST RESULTS SUMMARY")

        summary = report["summary"]

        print(f"{Colors.BOLD}Total Tests:{Colors.ENDC} {summary['total_tests']}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}Passed:{Colors.ENDC} {summary['passed']}")
        print(f"{Colors.FAIL}{Colors.BOLD}Failed:{Colors.ENDC} {summary['failed']}")
        print(f"{Colors.WARNING}Errors:{Colors.ENDC} {summary['total_errors']}")
        print(f"{Colors.WARNING}Warnings:{Colors.ENDC} {summary['total_warnings']}")
        print(f"{Colors.OKCYAN}Execution Time:{Colors.ENDC} {summary['total_execution_time']:.2f}s")
        print()

        # Production readiness score
        score = summary['production_readiness_score']
        level = summary['readiness_level']

        if score >= 90:
            color = Colors.OKGREEN
        elif score >= 75:
            color = Colors.OKCYAN
        elif score >= 60:
            color = Colors.WARNING
        else:
            color = Colors.FAIL

        print(f"{Colors.BOLD}Production Readiness Score:{Colors.ENDC} {color}{score}/100{Colors.ENDC}")
        print(f"{Colors.BOLD}Readiness Level:{Colors.ENDC} {color}{level}{Colors.ENDC}")
        print()

        # Bugs found
        if report["bugs_found"]:
            self.print_header("BUGS FOUND")
            for i, bug in enumerate(report["bugs_found"], 1):
                severity_color = Colors.FAIL if bug["severity"] == "high" else Colors.WARNING
                print(f"{i}. [{severity_color}{bug['severity'].upper()}{Colors.ENDC}] {bug['test']}")
                print(f"   {bug['error']}")
                print()

        # Recommendations
        if report["recommendations"]:
            self.print_header("RECOMMENDATIONS")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"{i}. {rec}")
            print()

        # User experience assessment
        self.print_header("USER EXPERIENCE ASSESSMENT")

        ux_score = "Good" if summary['total_warnings'] < 5 else "Needs Improvement"
        print(f"Overall UX: {ux_score}")
        print(f"- Clear error messages: {'Yes' if summary['total_errors'] < 3 else 'Needs improvement'}")
        print(f"- Proper file generation: {'Yes' if summary['passed'] > summary['failed'] else 'Issues detected'}")
        print(f"- Edge case handling: {'Good' if summary['total_errors'] < 5 else 'Needs improvement'}")
        print()


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent

    tester = EnvWizardRealWorldTester(base_dir)

    # Run all tests
    tester.run_all_tests()

    # Generate and print report
    report = tester.generate_report()
    tester.print_report(report)

    # Save report to JSON
    report_file = base_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"{Colors.OKGREEN}Full report saved to: {report_file}{Colors.ENDC}")

    # Exit with appropriate code
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
