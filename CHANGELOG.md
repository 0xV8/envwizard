# Changelog

All notable changes to envwizard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-02-11

### Added
- Initial release of envwizard
- Smart project type detection for popular Python frameworks
  - Django, FastAPI, Flask, Streamlit
  - Celery task queue
  - Data science tools (Pandas, NumPy)
  - Testing frameworks (pytest)
- Automatic framework detection from:
  - requirements.txt
  - pyproject.toml
  - Pipfile
  - Project file structure
- Virtual environment creation and management
  - Cross-platform support (Windows, macOS, Linux)
  - Python version specification
  - Automatic pip upgrade
- Intelligent .env file generation
  - Framework-specific environment variables
  - Database configuration (PostgreSQL, MySQL, MongoDB, Redis)
  - Smart placeholder values for sensitive data
  - Automatic .env.example creation
  - Organized sections with helpful comments
- Dependency installation from multiple sources
  - requirements.txt
  - pyproject.toml (Poetry, Hatch)
  - Pipfile (Pipenv)
- CLI commands:
  - `envwizard init` - Complete environment setup
  - `envwizard detect` - Project analysis without changes
  - `envwizard create-venv` - Virtual environment only
  - `envwizard create-dotenv` - .env files only
- Beautiful terminal UI using Rich
  - Progress indicators
  - Colored output
  - Informative panels and tables
  - ASCII art banner
- Automatic .gitignore management
  - Adds .env to .gitignore
  - Preserves existing .gitignore content
- Comprehensive test suite with >80% coverage
- Full documentation
  - README with usage examples
  - Contributing guidelines
  - API documentation via docstrings
- CI/CD pipeline with GitHub Actions
  - Multi-platform testing (Linux, macOS, Windows)
  - Python 3.8-3.12 support
  - Code quality checks (Black, Ruff, mypy)
  - Automated PyPI publishing

### Framework Support
- Django with database detection
- FastAPI with API configuration
- Flask with WSGI setup
- Streamlit with server configuration
- Celery with broker configuration
- PostgreSQL, MySQL, MongoDB, Redis databases

### Security
- No sensitive data in .env.example
- Automatic .gitignore configuration
- Security warnings in generated files
- Placeholder values for secrets

[Unreleased]: https://github.com/yourusername/envwizard/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/envwizard/releases/tag/v0.1.0
