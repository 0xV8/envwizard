# Contributing to envwizard

Thank you for considering contributing to envwizard! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Detailed steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, envwizard version)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- A clear and descriptive title
- A detailed description of the proposed feature
- Use cases and examples
- Any potential drawbacks or alternatives considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed
3. **Ensure tests pass**: Run `pytest` before submitting
4. **Update the changelog** if applicable
5. **Submit your pull request**

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/envwizard.git
cd envwizard

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Follow these guidelines:

- Write clear, self-documenting code
- Add docstrings to all public functions and classes
- Follow PEP 8 style guidelines
- Keep functions focused and single-purpose
- Add type hints where appropriate

### 3. Write Tests

All new features and bug fixes should include tests:

```python
# tests/test_your_feature.py
import pytest
from envwizard import EnvWizard

def test_your_new_feature():
    """Test description."""
    wizard = EnvWizard()
    result = wizard.your_new_method()
    assert result == expected_value
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=envwizard --cov-report=html

# Run specific test file
pytest tests/test_your_feature.py

# Run tests with verbose output
pytest -v
```

### 5. Check Code Quality

```bash
# Format code with black
black src/envwizard tests

# Check linting with ruff
ruff check src/envwizard tests

# Run type checking
mypy src/envwizard
```

### 6. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: smart template detection for React projects"
```

Commit message guidelines:
- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Add a blank line before detailed description if needed
- Reference issues and pull requests when applicable

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- A clear title
- Description of changes
- Related issue numbers (if applicable)
- Screenshots or examples (if applicable)

## Code Style Guidelines

### Python Style

We follow PEP 8 with these specifics:

- **Line length**: 100 characters
- **Indentation**: 4 spaces
- **Quotes**: Prefer double quotes for strings
- **Imports**: Group in order: standard library, third-party, local

### Type Hints

Use type hints for function signatures:

```python
from typing import Optional, List, Tuple
from pathlib import Path

def create_venv(
    self,
    venv_name: str = "venv",
    python_version: Optional[str] = None
) -> Tuple[bool, str, Path]:
    """Create a virtual environment."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def generate_dotenv(
    self,
    frameworks: List[str],
    output_file: str = ".env",
) -> Tuple[bool, str]:
    """
    Generate .env file based on detected frameworks.

    Args:
        frameworks: List of detected frameworks
        output_file: Output filename (default: .env)

    Returns:
        Tuple of (success, message)

    Raises:
        ValueError: If frameworks list is empty

    Example:
        >>> generator = DotEnvGenerator()
        >>> success, msg = generator.generate_dotenv(["django"])
        >>> print(msg)
        Created .env and .env.example
    """
    pass
```

## Testing Guidelines

### Test Structure

Organize tests by module:

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_core.py         # Core functionality tests
├── test_detectors.py    # Detector tests
├── test_venv.py         # Virtual environment tests
└── test_dotenv.py       # .env generation tests
```

### Writing Good Tests

- **One assertion per test** when possible
- **Clear test names**: `test_should_detect_django_when_manage_py_exists`
- **Use fixtures** for common setup
- **Test edge cases** and error conditions
- **Mock external dependencies** when appropriate

### Test Coverage

Aim for at least 80% code coverage. Check coverage with:

```bash
pytest --cov=envwizard --cov-report=term-missing
```

## Documentation

### Code Documentation

- Add docstrings to all public APIs
- Include usage examples in docstrings
- Document exceptions that can be raised
- Keep docstrings up-to-date with code changes

### README and Guides

- Update README.md for new features
- Add examples for new functionality
- Update CLI help text if commands change
- Create guides for complex features

## Project Structure

```
envwizard/
├── src/envwizard/
│   ├── __init__.py
│   ├── core.py              # Main EnvWizard class
│   ├── venv.py              # Virtual environment management
│   ├── detectors/           # Project and framework detection
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── framework.py
│   │   └── dependency.py
│   ├── generators/          # File generators
│   │   ├── __init__.py
│   │   └── dotenv.py
│   └── cli/                 # CLI interface
│       ├── __init__.py
│       └── main.py
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
└── README.md
```

## Adding New Framework Support

To add support for a new framework:

1. **Add framework detection** in `src/envwizard/detectors/framework.py`:

```python
FRAMEWORK_CONFIG = {
    "your_framework": {
        "env_vars": [
            ("FRAMEWORK_VAR", "default_value"),
        ],
        "description": "Your framework description",
    },
}
```

2. **Add detection logic** in `src/envwizard/detectors/base.py`:

```python
FRAMEWORK_INDICATORS = {
    "your_framework": ["indicator_file.py", "framework_package"],
}
```

3. **Add tests** in `tests/test_detectors.py`

4. **Update documentation** in README.md

## Release Process

Maintainers follow this process for releases:

1. Update version in `pyproject.toml` and `src/envwizard/__init__.py`
2. Update CHANGELOG.md
3. Create and push a git tag
4. GitHub Actions will automatically publish to PyPI
5. Create a GitHub release with release notes

## Questions?

- Open an issue for questions about contributing
- Join our discussions on GitHub Discussions
- Check existing issues and pull requests

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- The project's contributors page

Thank you for contributing to envwizard!
