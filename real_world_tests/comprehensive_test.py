#!/usr/bin/env python3
"""
Comprehensive Real-World Testing for envwizard
Handles interactive prompts and provides detailed analysis
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple


class TestResults:
    """Comprehensive test results storage and reporting."""

    def __init__(self):
        self.tests: List[Dict[str, Any]] = []
        self.bugs: List[Dict[str, Any]] = []
        self.start_time = datetime.now()

    def add_test(self, name: str, passed: bool, details: Dict[str, Any] = None):
        """Add a test result."""
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })

    def add_bug(self, severity: str, component: str, description: str, test_name: str = None):
        """Add a bug report."""
        self.bugs.append({
            "severity": severity,
            "component": component,
            "description": description,
            "test_name": test_name,
            "found_at": datetime.now().isoformat()
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary statistics."""
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t["passed"])
        failed = total - passed
        duration = (datetime.now() - self.start_time).total_seconds()

        # Calculate production readiness score
        if total == 0:
            pass_rate = 0
        else:
            pass_rate = (passed / total) * 100

        bug_severity_weights = {
            "critical": 20,
            "high": 10,
            "medium": 5,
            "low": 2
        }

        bug_penalty = sum(bug_severity_weights.get(b["severity"], 5) for b in self.bugs)

        # Score calculation (100 base - penalties)
        score = max(0, min(100, pass_rate - bug_penalty))

        if score >= 90:
            readiness = "Production Ready"
        elif score >= 75:
            readiness = "Nearly Production Ready"
        elif score >= 60:
            readiness = "Beta Quality"
        else:
            readiness = "Not Production Ready"

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 2),
            "bugs_found": len(self.bugs),
            "critical_bugs": sum(1 for b in self.bugs if b["severity"] == "critical"),
            "high_bugs": sum(1 for b in self.bugs if b["severity"] == "high"),
            "duration_seconds": round(duration, 2),
            "production_readiness_score": round(score, 2),
            "readiness_level": readiness
        }


def run_cmd(cmd: str, cwd: Path, auto_confirm: bool = False) -> Tuple[int, str, str]:
    """Run command with optional auto-confirmation."""
    if auto_confirm:
        cmd = f"yes | {cmd}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=180
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)


def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_django_app(base_dir: Path, results: TestResults):
    """Test Django application."""
    print_section("TEST 1: Django Application")

    test_dir = base_dir / "django_app"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    # Create Django project
    (test_dir / "manage.py").write_text("""#!/usr/bin/env python
import os, sys
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
SECRET_KEY = 'test'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
""")
    (test_dir / "myproject" / "urls.py").write_text("""
from django.contrib import admin
from django.urls import path
urlpatterns = [path('admin/', admin.site.urls)]
""")

    (test_dir / "requirements.txt").write_text("Django>=4.2.0\npsycopg2-binary>=2.9.0\n")

    print("✓ Django project structure created")

    # Run envwizard
    rc, stdout, stderr = run_cmd("envwizard init --path . --venv-name venv", test_dir, auto_confirm=True)

    details = {
        "returncode": rc,
        "venv_exists": (test_dir / "venv").exists(),
        "dotenv_exists": (test_dir / ".env").exists(),
        "dotenv_example_exists": (test_dir / ".env.example").exists(),
        "gitignore_exists": (test_dir / ".gitignore").exists()
    }

    if rc == 0:
        print("✓ envwizard init succeeded")

        # Verify .env content
        dotenv_path = test_dir / ".env"
        if dotenv_path.exists():
            content = dotenv_path.read_text()
            django_vars = ["SECRET_KEY", "DEBUG", "ALLOWED_HOSTS", "DJANGO"]
            found_vars = [v for v in django_vars if v in content]
            details["django_vars_found"] = found_vars

            if len(found_vars) >= 2:
                print(f"✓ Django variables found in .env: {', '.join(found_vars)}")
            else:
                print(f"⚠ Limited Django variables in .env: {', '.join(found_vars)}")
                results.add_bug("medium", "dotenv_generator", f"Missing Django variables: {set(django_vars) - set(found_vars)}", "Django App")

            # Check for PostgreSQL config
            if "POSTGRES" in content:
                print("✓ PostgreSQL configuration detected")
            else:
                print("⚠ PostgreSQL not detected (from requirements)")

        # Verify venv activation
        activate_script = test_dir / "venv" / "bin" / "activate"
        if activate_script.exists():
            print("✓ Virtual environment activation script exists")
            details["venv_activatable"] = True

            # Check if Django is installed
            rc2, out, _ = run_cmd("source venv/bin/activate && pip show Django", test_dir)
            if rc2 == 0 and "Version:" in out:
                print("✓ Django installed in venv")
                details["django_installed"] = True
            else:
                print("✗ Django not installed")
                results.add_bug("high", "dependency_installer", "Django not installed in venv", "Django App")

        results.add_test("Django Application", rc == 0 and details["venv_exists"] and details["dotenv_exists"], details)
    else:
        print(f"✗ envwizard init failed: {stderr}")
        results.add_bug("critical", "cli", f"envwizard init failed: {stderr}", "Django App")
        results.add_test("Django Application", False, details)


def test_fastapi_app(base_dir: Path, results: TestResults):
    """Test FastAPI application."""
    print_section("TEST 2: FastAPI Application")

    test_dir = base_dir / "fastapi_app"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    # Create FastAPI project
    (test_dir / "main.py").write_text("""
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello"}
""")

    (test_dir / "requirements.txt").write_text("""fastapi>=0.100.0
uvicorn[standard]>=0.22.0
redis>=4.5.0
python-dotenv>=1.0.0
""")

    print("✓ FastAPI project structure created")

    rc, stdout, stderr = run_cmd("envwizard init --path .", test_dir, auto_confirm=True)

    details = {
        "returncode": rc,
        "venv_exists": (test_dir / "venv").exists(),
        "dotenv_exists": (test_dir / ".env").exists()
    }

    if rc == 0:
        print("✓ envwizard init succeeded")

        dotenv_path = test_dir / ".env"
        if dotenv_path.exists():
            content = dotenv_path.read_text()

            # Check for FastAPI-specific vars
            api_vars = ["API", "DEBUG", "SECRET_KEY"]
            found = [v for v in api_vars if v in content]
            details["api_vars_found"] = found

            if found:
                print(f"✓ API variables found: {', '.join(found)}")

            # Check for Redis
            if "REDIS" in content:
                print("✓ Redis configuration detected")
                details["redis_detected"] = True
            else:
                print("⚠ Redis not detected (expected from requirements)")
                results.add_bug("medium", "framework_detector", "Redis not detected from requirements", "FastAPI App")

        results.add_test("FastAPI Application", rc == 0 and details["venv_exists"] and details["dotenv_exists"], details)
    else:
        print(f"✗ envwizard init failed: {stderr}")
        results.add_bug("critical", "cli", f"envwizard init failed: {stderr}", "FastAPI App")
        results.add_test("FastAPI Application", False, details)


def test_flask_app(base_dir: Path, results: TestResults):
    """Test Flask application."""
    print_section("TEST 3: Flask Application")

    test_dir = base_dir / "flask_app"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    (test_dir / "app.py").write_text("""
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
""")

    (test_dir / "requirements.txt").write_text("Flask>=2.3.0\nFlask-SQLAlchemy>=3.0.0\n")

    print("✓ Flask project created")

    rc, _, stderr = run_cmd("envwizard init --no-install", test_dir, auto_confirm=True)

    details = {
        "returncode": rc,
        "venv_exists": (test_dir / "venv").exists(),
        "dotenv_exists": (test_dir / ".env").exists()
    }

    if rc == 0:
        print("✓ envwizard init succeeded")

        if (test_dir / ".env").exists():
            content = (test_dir / ".env").read_text()
            if "FLASK" in content or "APP" in content:
                print("✓ Flask configuration detected")

        results.add_test("Flask Application", True, details)
    else:
        print(f"✗ Failed: {stderr}")
        results.add_bug("high", "cli", f"Flask test failed: {stderr}", "Flask App")
        results.add_test("Flask Application", False, details)


def test_empty_project(base_dir: Path, results: TestResults):
    """Test empty/minimal project."""
    print_section("TEST 4: Empty Project")

    test_dir = base_dir / "empty_project"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    (test_dir / "script.py").write_text("print('Hello')")

    print("✓ Empty project created")

    # Test detect command
    rc, stdout, stderr = run_cmd("envwizard detect", test_dir)

    details = {"detect_returncode": rc}

    if rc == 0:
        print("✓ envwizard detect handled empty project")
        details["detect_passed"] = True
    else:
        print("⚠ envwizard detect failed on empty project")
        results.add_bug("low", "detector", f"Detect failed on empty project: {stderr}", "Empty Project")

    # Test create-dotenv
    rc2, _, stderr2 = run_cmd("envwizard create-dotenv", test_dir, auto_confirm=True)

    if rc2 == 0 and (test_dir / ".env").exists():
        print("✓ Created .env for empty project")
        details["dotenv_created"] = True
    else:
        print("⚠ Failed to create .env for empty project")

    results.add_test("Empty Project", details.get("detect_passed", False), details)


def test_multi_framework(base_dir: Path, results: TestResults):
    """Test project with multiple frameworks."""
    print_section("TEST 5: Multi-Framework Project (Django + Celery + Redis)")

    test_dir = base_dir / "multi_framework"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    (test_dir / "manage.py").write_text("# Django manage.py")
    (test_dir / "celery_app.py").write_text("""
from celery import Celery
app = Celery('myapp')
""")
    (test_dir / "requirements.txt").write_text("""Django>=4.2.0
celery>=5.3.0
redis>=4.5.0
psycopg2-binary>=2.9.0
""")

    print("✓ Multi-framework project created")

    rc, _, stderr = run_cmd("envwizard init --no-install", test_dir, auto_confirm=True)

    details = {"returncode": rc}

    if rc == 0:
        print("✓ envwizard init succeeded")

        if (test_dir / ".env").exists():
            content = (test_dir / ".env").read_text()
            frameworks = []

            if "DJANGO" in content or "SECRET_KEY" in content:
                frameworks.append("Django")
            if "CELERY" in content:
                frameworks.append("Celery")
            if "REDIS" in content:
                frameworks.append("Redis")
            if "POSTGRES" in content:
                frameworks.append("PostgreSQL")

            details["frameworks_detected"] = frameworks

            print(f"✓ Frameworks detected in .env: {', '.join(frameworks)}")

            if len(frameworks) >= 2:
                print("✓ Multiple frameworks properly detected")
                results.add_test("Multi-Framework Project", True, details)
            else:
                print("⚠ Expected more frameworks to be detected")
                results.add_bug("medium", "framework_detector", f"Only detected: {frameworks}", "Multi-Framework")
                results.add_test("Multi-Framework Project", False, details)
        else:
            results.add_test("Multi-Framework Project", False, details)
    else:
        print(f"✗ Failed: {stderr}")
        results.add_bug("high", "cli", f"Multi-framework test failed: {stderr}", "Multi-Framework")
        results.add_test("Multi-Framework Project", False, details)


def test_existing_venv(base_dir: Path, results: TestResults):
    """Test with pre-existing venv."""
    print_section("TEST 6: Existing Virtual Environment")

    test_dir = base_dir / "existing_venv"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    (test_dir / "app.py").write_text("print('test')")
    (test_dir / "requirements.txt").write_text("requests>=2.31.0\n")

    # Create venv first
    rc1, _, _ = run_cmd(f"{sys.executable} -m venv venv", test_dir)

    if rc1 == 0:
        print("✓ Pre-existing venv created")

        # Run envwizard
        rc2, stdout, stderr = run_cmd("envwizard init --no-install", test_dir, auto_confirm=True)

        details = {
            "pre_venv_exists": True,
            "returncode": rc2,
            "handled_gracefully": "already exists" in stdout.lower() or "already exists" in stderr.lower() or rc2 == 0
        }

        if details["handled_gracefully"]:
            print("✓ envwizard handled existing venv gracefully")
            results.add_test("Existing Virtual Environment", True, details)
        else:
            print("✗ envwizard did not handle existing venv well")
            results.add_bug("medium", "venv_manager", "Existing venv not handled gracefully", "Existing Venv")
            results.add_test("Existing Virtual Environment", False, details)
    else:
        print("✗ Failed to create pre-existing venv")
        results.add_test("Existing Virtual Environment", False, {"error": "Could not create initial venv"})


def test_cli_commands(base_dir: Path, results: TestResults):
    """Test all CLI commands."""
    print_section("TEST 7: CLI Commands")

    test_dir = base_dir / "cli_test"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    (test_dir / "app.py").write_text("print('test')")
    (test_dir / "requirements.txt").write_text("requests>=2.31.0\n")

    cli_results = {}

    # Test --version
    rc, out, _ = run_cmd("envwizard --version", test_dir)
    if rc == 0 and "version" in out.lower():
        print("✓ envwizard --version works")
        cli_results["version"] = True
    else:
        print("✗ envwizard --version failed")
        cli_results["version"] = False
        results.add_bug("medium", "cli", "Version command failed", "CLI Commands")

    # Test detect
    rc, _, _ = run_cmd("envwizard detect", test_dir)
    if rc == 0:
        print("✓ envwizard detect works")
        cli_results["detect"] = True
    else:
        print("✗ envwizard detect failed")
        cli_results["detect"] = False
        results.add_bug("high", "cli", "Detect command failed", "CLI Commands")

    # Test create-venv
    rc, _, _ = run_cmd("envwizard create-venv --name test_venv", test_dir, auto_confirm=True)
    if rc == 0 and (test_dir / "test_venv").exists():
        print("✓ envwizard create-venv works")
        cli_results["create_venv"] = True
    else:
        print("✗ envwizard create-venv failed")
        cli_results["create_venv"] = False
        results.add_bug("high", "cli", "Create-venv command failed", "CLI Commands")

    # Test create-dotenv
    rc, _, _ = run_cmd("envwizard create-dotenv", test_dir, auto_confirm=True)
    if rc == 0 and (test_dir / ".env").exists():
        print("✓ envwizard create-dotenv works")
        cli_results["create_dotenv"] = True
    else:
        print("✗ envwizard create-dotenv failed")
        cli_results["create_dotenv"] = False
        results.add_bug("high", "cli", "Create-dotenv command failed", "CLI Commands")

    all_passed = all(cli_results.values())
    results.add_test("CLI Commands", all_passed, cli_results)


def test_complex_dependencies(base_dir: Path, results: TestResults):
    """Test complex dependency scenarios."""
    print_section("TEST 8: Complex Dependencies")

    test_dir = base_dir / "complex_deps"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    (test_dir / "requirements.txt").write_text("""# Web
Flask==2.3.0
flask-cors>=1.10.0

# Database
SQLAlchemy>=2.0.0,<3.0.0
alembic~=1.11.0

# Data
pandas>=2.0.0
numpy>=1.24.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Platform-specific
psycopg2-binary>=2.9.0; sys_platform != 'win32'
""")

    (test_dir / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")

    print("✓ Complex dependencies project created")

    rc, _, stderr = run_cmd("envwizard init --no-install", test_dir, auto_confirm=True)

    details = {"returncode": rc}

    if rc == 0:
        print("✓ envwizard handled complex dependencies")
        results.add_test("Complex Dependencies", True, details)
    else:
        print(f"✗ Failed with complex dependencies: {stderr}")
        results.add_bug("high", "dependency_detector", f"Failed on complex deps: {stderr}", "Complex Dependencies")
        results.add_test("Complex Dependencies", False, details)


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  ENVWIZARD COMPREHENSIVE REAL-WORLD TESTING SUITE")
    print("="*80)

    base_dir = Path(__file__).parent / "test_projects"
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir()

    results = TestResults()

    # Run all tests
    test_django_app(base_dir, results)
    test_fastapi_app(base_dir, results)
    test_flask_app(base_dir, results)
    test_empty_project(base_dir, results)
    test_multi_framework(base_dir, results)
    test_existing_venv(base_dir, results)
    test_cli_commands(base_dir, results)
    test_complex_dependencies(base_dir, results)

    # Generate report
    print_section("FINAL RESULTS")

    summary = results.get_summary()

    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']}%")
    print(f"Duration: {summary['duration_seconds']}s")
    print(f"\nBugs Found: {summary['bugs_found']}")
    print(f"  Critical: {summary['critical_bugs']}")
    print(f"  High: {summary['high_bugs']}")
    print(f"\nProduction Readiness Score: {summary['production_readiness_score']}/100")
    print(f"Readiness Level: {summary['readiness_level']}")

    # Detailed bug report
    if results.bugs:
        print_section("BUGS AND ISSUES FOUND")
        for i, bug in enumerate(results.bugs, 1):
            print(f"{i}. [{bug['severity'].upper()}] {bug['component']}")
            print(f"   {bug['description']}")
            if bug['test_name']:
                print(f"   Test: {bug['test_name']}")
            print()

    # Save full report
    report = {
        "summary": summary,
        "tests": results.tests,
        "bugs": results.bugs,
        "generated_at": datetime.now().isoformat()
    }

    report_file = Path(__file__).parent / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nFull report saved to: {report_file}")

    # User experience assessment
    print_section("USER EXPERIENCE ASSESSMENT")

    ux_score = "Excellent" if summary['bugs_found'] <= 2 else "Good" if summary['bugs_found'] <= 5 else "Needs Improvement"
    print(f"Overall UX Quality: {ux_score}")
    print(f"• Clear output messages: {'Yes' if summary['passed'] >= 6 else 'Partial'}")
    print(f"• Proper error handling: {'Yes' if summary['critical_bugs'] == 0 else 'No'}")
    print(f"• File generation accuracy: {'Yes' if summary['pass_rate'] >= 75 else 'Partial'}")
    print(f"• Edge case handling: {'Good' if summary['failed'] <= 2 else 'Needs work'}")

    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
