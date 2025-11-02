# envwizard - Developer Documentation

Internal documentation for envwizard developers and contributors.

## Project Architecture

### Directory Structure

```
envwizard/
├── src/envwizard/          # Main package source
│   ├── __init__.py         # Package initialization
│   ├── core.py             # Core EnvWizard class
│   ├── venv.py             # Virtual environment management
│   ├── detectors/          # Project detection modules
│   │   ├── __init__.py
│   │   ├── base.py         # Base project detector
│   │   ├── framework.py    # Framework-specific configs
│   │   └── dependency.py   # Dependency detection
│   ├── generators/         # File generators
│   │   ├── __init__.py
│   │   └── dotenv.py       # .env file generation
│   └── cli/                # Command-line interface
│       ├── __init__.py
│       └── main.py         # CLI commands and UI
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── test_core.py
│   ├── test_detectors.py
│   ├── test_venv.py
│   └── test_dotenv.py
├── docs/                   # Documentation (future)
├── .github/                # GitHub configurations
│   ├── workflows/          # CI/CD workflows
│   └── ISSUE_TEMPLATE/     # Issue templates
├── pyproject.toml          # Project configuration
├── README.md               # User documentation
├── CONTRIBUTING.md         # Contribution guidelines
├── CHANGELOG.md            # Version history
├── LICENSE                 # MIT License
└── Makefile               # Development commands
```

## Component Overview

### Core Module (`core.py`)

The `EnvWizard` class orchestrates all functionality:

```python
class EnvWizard:
    def __init__(self, project_path: Optional[Path] = None)
    def setup(self, venv_name, install_deps, create_dotenv) -> Dict
    def get_project_info(self) -> Dict
    def create_venv_only(self, venv_name, python_version) -> Tuple
    def create_dotenv_only(self, frameworks) -> Tuple
    def install_dependencies_only(self, venv_path) -> Tuple
```

### Detectors Module

#### ProjectDetector (`detectors/base.py`)
- Detects project type and characteristics
- Scans for framework indicators in files and structure
- Returns comprehensive project information

#### FrameworkDetector (`detectors/framework.py`)
- Provides framework-specific configurations
- Maintains environment variable templates
- Detects database types

#### DependencyDetector (`detectors/dependency.py`)
- Finds and parses dependency files
- Supports requirements.txt, pyproject.toml, Pipfile
- Extracts dependency lists

### Virtual Environment Module (`venv.py`)

```python
class VirtualEnvManager:
    def create_venv(self, venv_name, python_version) -> Tuple
    def install_dependencies(self, venv_path, requirements_file) -> Tuple
    def install_package(self, venv_path, package) -> Tuple
    def get_activation_command(self, venv_path) -> str
    def get_python_executable(self, venv_path) -> Path
    def get_pip_executable(self, venv_path) -> Path
```

### Generators Module

#### DotEnvGenerator (`generators/dotenv.py`)
- Generates .env and .env.example files
- Organizes variables into logical sections
- Handles sensitive data with placeholders
- Validates .env files

### CLI Module (`cli/main.py`)

Commands:
- `envwizard init`: Complete setup
- `envwizard detect`: Project analysis
- `envwizard create-venv`: Create virtual environment
- `envwizard create-dotenv`: Generate .env files

Uses Rich library for beautiful terminal UI.

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/envwizard.git
cd envwizard

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=envwizard --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::TestEnvWizard::test_setup_django_project

# Run with verbose output
pytest -v

# Run with output printing
pytest -s
```

### Code Quality Tools

```bash
# Format code
black src/envwizard tests

# Check formatting without changes
black --check src/envwizard tests

# Lint with ruff
ruff check src/envwizard tests

# Fix linting issues
ruff check --fix src/envwizard tests

# Type checking
mypy src/envwizard
```

### Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:
- Trailing whitespace removal
- End of file fixer
- YAML/TOML validation
- Black formatting
- Ruff linting
- Mypy type checking

```bash
# Run manually on all files
pre-commit run --all-files
```

## Adding New Features

### Adding Framework Support

1. **Update Framework Configuration** (`detectors/framework.py`):

```python
FRAMEWORK_CONFIG = {
    "newframework": {
        "env_vars": [
            ("FRAMEWORK_VAR", "default_value"),
            ("ANOTHER_VAR", "value"),
        ],
        "description": "Description of the framework",
    },
}
```

2. **Add Detection Logic** (`detectors/base.py`):

```python
FRAMEWORK_INDICATORS = {
    "newframework": ["indicator_file.py", "package_name"],
}
```

3. **Write Tests** (`tests/test_detectors.py`):

```python
def test_detect_newframework(self, temp_project_dir):
    # Create framework files
    (temp_project_dir / "indicator_file.py").write_text("...")

    detector = ProjectDetector(temp_project_dir)
    info = detector.detect_project_type()

    assert "newframework" in info["frameworks"]
```

4. **Update Documentation**:
- Add to README.md supported frameworks list
- Add example in documentation

### Adding CLI Commands

1. **Add Command** (`cli/main.py`):

```python
@cli.command()
@click.option("--option", help="Option description")
def new_command(option: str) -> None:
    """Command description."""
    # Implementation
    pass
```

2. **Write Tests**:

```python
from click.testing import CliRunner
from envwizard.cli.main import cli

def test_new_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['new-command', '--option', 'value'])
    assert result.exit_code == 0
```

## Testing Strategy

### Unit Tests

Test individual functions and methods in isolation:

```python
def test_parse_requirements(self, temp_project_dir):
    req_file = temp_project_dir / "requirements.txt"
    req_file.write_text("django>=4.0\ncelery>=5.0\n")

    detector = DependencyDetector(temp_project_dir)
    packages = detector.parse_requirements(req_file)

    assert "django>=4.0" in packages
    assert "celery>=5.0" in packages
```

### Integration Tests

Test multiple components working together:

```python
def test_setup_django_project(self, django_project):
    wizard = EnvWizard(django_project)
    results = wizard.setup(venv_name="test_venv")

    assert results["venv_created"] is True
    assert results["dotenv_created"] is True
    assert (django_project / ".env").exists()
```

### Fixtures

Defined in `tests/conftest.py`:

```python
@pytest.fixture
def django_project(temp_project_dir):
    """Create a mock Django project."""
    (temp_project_dir / "manage.py").write_text("...")
    (temp_project_dir / "requirements.txt").write_text("django>=4.0")
    return temp_project_dir
```

## Performance Considerations

### File System Operations

- Use `pathlib.Path` for cross-platform compatibility
- Cache file reads when possible
- Limit directory traversal depth

### Virtual Environment Creation

- Use built-in `venv` module when possible
- Subprocess calls are blocking - consider async for future

### Dependency Installation

- Installation can be slow - provide progress feedback
- Consider parallel installation for future enhancement

## Security Considerations

### Environment Variables

- Never include sensitive values in .env.example
- Add .env to .gitignore automatically
- Warn users about sensitive data

### Virtual Environments

- Always create isolated environments
- Don't execute arbitrary code from dependencies
- Validate Python executable paths

### File Operations

- Validate file paths to prevent directory traversal
- Don't overwrite files without confirmation
- Use appropriate file permissions

## Common Development Tasks

### Adding a Test

```python
# tests/test_new_feature.py
import pytest
from envwizard import EnvWizard

def test_new_feature(temp_project_dir):
    """Test description."""
    wizard = EnvWizard(temp_project_dir)
    result = wizard.new_method()
    assert result == expected_value
```

### Debugging

```python
# Add to code for debugging
import pdb; pdb.set_trace()

# Or use pytest with pdb
pytest --pdb tests/test_file.py

# Print debugging
pytest -s tests/test_file.py
```

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
wizard.setup()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Release Checklist

See `RELEASE.md` for complete checklist. Quick reference:

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Build package
5. Test on TestPyPI
6. Create git tag
7. Create GitHub release
8. Publish to PyPI

## Useful Resources

### Documentation
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)

### Tools
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

## Getting Help

- Check existing issues on GitHub
- Read CONTRIBUTING.md
- Ask in GitHub Discussions
- Review test cases for examples

## Future Enhancements

- Support for more frameworks (Node.js, Rust, etc.)
- Docker configuration generation
- Cloud deployment helpers
- Interactive setup wizard
- Configuration file for custom templates
- Plugin system for extensibility
