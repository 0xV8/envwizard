# envwizard

**Smart Environment Setup Tool** - One command to create virtual environments, install dependencies, and configure `.env` intelligently.

[![PyPI version](https://badge.fury.io/py/envwizard.svg)](https://badge.fury.io/py/envwizard)
[![Python Support](https://img.shields.io/pypi/pyversions/envwizard.svg)](https://pypi.org/project/envwizard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/envwizard/workflows/tests/badge.svg)](https://github.com/yourusername/envwizard/actions)

---

## Why envwizard?

Developers waste valuable time setting up development environments. **envwizard** automates the entire process:

- Automatically detects your project type (Django, FastAPI, Flask, and more)
- Creates virtual environments with the right Python version
- Installs all dependencies from requirements files
- Generates `.env` and `.env.example` with intelligent defaults
- Cross-platform support (Windows, macOS, Linux)
- Beautiful, informative CLI output

## Features

- **Smart Project Detection**: Automatically identifies frameworks like Django, FastAPI, Flask, Streamlit, Celery, and more
- **Intelligent .env Generation**: Creates environment files with framework-specific variables and smart defaults
- **Virtual Environment Management**: Creates and configures virtual environments with ease
- **Dependency Installation**: Automatically installs dependencies from `requirements.txt`, `pyproject.toml`, or `Pipfile`
- **Database Detection**: Identifies and configures environment variables for PostgreSQL, MySQL, MongoDB, and Redis
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **Beautiful Output**: Rich terminal UI with progress indicators and helpful messages
- **Git Integration**: Automatically adds `.env` to `.gitignore` for security

## Installation

```bash
pip install envwizard
```

Or install from source:

```bash
git clone https://github.com/yourusername/envwizard.git
cd envwizard
pip install -e .
```

## Quick Start

Navigate to your project directory and run:

```bash
envwizard init
```

That's it! envwizard will:

1. Analyze your project and detect frameworks
2. Create a virtual environment
3. Install all dependencies
4. Generate `.env` and `.env.example` files
5. Add `.env` to `.gitignore`

### Example Output

```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███████╗███╗   ██╗██╗   ██╗██╗    ██╗██╗███████╗      ║
    ║   ██╔════╝████╗  ██║██║   ██║██║    ██║██║╚══███╔╝      ║
    ║   █████╗  ██╔██╗ ██║██║   ██║██║ █╗ ██║██║  ███╔╝       ║
    ║   ██╔══╝  ██║╚██╗██║╚██╗ ██╔╝██║███╗██║██║ ███╔╝        ║
    ║   ███████╗██║ ╚████║ ╚████╔╝ ╚███╔███╔╝██║███████╗      ║
    ║   ╚══════╝╚═╝  ╚═══╝  ╚═══╝   ╚══╝╚══╝ ╚═╝╚══════╝      ║
    ║                                                           ║
    ║          Smart Environment Setup Tool                     ║
    ╚═══════════════════════════════════════════════════════════╝

Project path: /path/to/your/project

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property          ┃ Value                                  ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Frameworks        │ django, celery, postgresql             │
│ Dependency Files  │ requirements.txt                       │
│ Python Version    │ >=3.8                                  │
└───────────────────┴────────────────────────────────────────┘

✓ Virtual environment created
✓ Dependencies installed
✓ .env files created

┌─ Next Step: Activate Virtual Environment ─────────────────┐
│ source venv/bin/activate                                   │
└────────────────────────────────────────────────────────────┘
```

## Usage

### Initialize Complete Environment

```bash
envwizard init
```

Options:
- `--path, -p`: Specify project directory (default: current directory)
- `--venv-name, -n`: Virtual environment name (default: venv)
- `--no-install`: Skip dependency installation
- `--no-dotenv`: Skip .env file generation
- `--python-version`: Specify Python version (e.g., 3.11)

Example:
```bash
envwizard init --path /path/to/project --venv-name .venv --python-version 3.11
```

### Detect Project Type

Analyze your project without making any changes:

```bash
envwizard detect
```

### Create Virtual Environment Only

```bash
envwizard create-venv --name .venv
```

### Generate .env Files Only

```bash
envwizard create-dotenv
```

## Supported Frameworks

envwizard automatically detects and configures environment variables for:

- **Web Frameworks**: Django, FastAPI, Flask, Streamlit
- **Task Queues**: Celery
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Data Science**: Pandas, NumPy
- **Testing**: pytest
- **Package Management**: Poetry, Pipenv

## Generated .env Structure

envwizard generates well-organized `.env` files with:

- Framework-specific variables
- Database configuration
- Security settings
- API and network configuration
- Helpful comments and sections
- Placeholder values for sensitive data

### Example .env for Django + PostgreSQL

```env
# Environment Configuration
# Auto-generated by envwizard

# Detected frameworks:
#   - django: Django web framework detected
#   - postgresql: Database detected

# Application Settings
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Security & Authentication
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=myapp
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme

# Add your custom environment variables below
```

## Advanced Usage

### Custom Project Setup

```python
from envwizard import EnvWizard
from pathlib import Path

# Initialize wizard
wizard = EnvWizard(Path("/path/to/project"))

# Get project information
info = wizard.get_project_info()
print(f"Detected frameworks: {info['frameworks']}")

# Perform complete setup
results = wizard.setup(
    venv_name="venv",
    install_deps=True,
    create_dotenv=True
)

print(f"Activation command: {results['activation_command']}")
```

### Individual Operations

```python
from envwizard import EnvWizard

wizard = EnvWizard()

# Create virtual environment only
success, message, venv_path = wizard.create_venv_only("my_venv")

# Generate .env files only
success, message = wizard.create_dotenv_only(frameworks=["fastapi", "redis"])

# Install dependencies only
success, message = wizard.install_dependencies_only(venv_path)
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/envwizard.git
cd envwizard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
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

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/envwizard tests

# Lint code
ruff check src/envwizard tests

# Type checking
mypy src/envwizard
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Roadmap

- [ ] Support for more frameworks (Next.js, React, Vue, etc.)
- [ ] Docker configuration generation
- [ ] Cloud deployment helpers (AWS, GCP, Azure)
- [ ] Environment variable validation and suggestions
- [ ] Interactive configuration wizard
- [ ] Template system for custom project types
- [ ] VS Code extension integration

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- Inspired by the need to simplify Python development workflows

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/envwizard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/envwizard/discussions)
- **Documentation**: [Full Documentation](https://github.com/yourusername/envwizard#readme)

---

Made with ❤️ for the Python community
