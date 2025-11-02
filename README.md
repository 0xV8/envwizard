# 🧙‍♂️ EnvWizard

**Smart environment setup tool for Python projects** - One command to create virtual environments, install dependencies, and configure .env files intelligently.

[![PyPI version](https://badge.fury.io/py/envwizard.svg)](https://pypi.org/project/envwizard/)
[![Python Support](https://img.shields.io/pypi/pyversions/envwizard.svg)](https://pypi.org/project/envwizard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-100%20passing-brightgreen.svg)](https://github.com/0xV8/envwizard)
[![Coverage](https://img.shields.io/badge/coverage-76%25-green.svg)](https://github.com/0xV8/envwizard)
[![Security](https://img.shields.io/badge/security-A+-brightgreen.svg)](https://github.com/0xV8/envwizard)

## ✨ Features

- 🔍 **Auto-Detection** - Automatically detects Django, FastAPI, Flask, and 20+ frameworks
- 🎯 **Smart .env Generation** - Creates comprehensive .env files with framework-specific variables
- 🐍 **Virtual Environment Management** - Creates and manages venvs with specific Python versions
- 📦 **Dependency Installation** - Auto-installs from requirements.txt, pyproject.toml, or Pipfile
- 🎨 **Beautiful CLI** - Rich terminal output with colors and progress indicators
- 🔒 **Secure by Default** - Input validation, path protection, secure file permissions
- 🚀 **Cross-Platform** - Works on Linux, macOS, and Windows
- ⚡ **Fast** - Saves 95% of setup time (15-30 min → 30 seconds)

## 📦 Installation

```bash
pip install envwizard
```

## 🚀 Quick Start

### Initialize a New Project

```bash
# Navigate to your project directory
cd my-django-project

# Run envwizard
envwizard init

# That's it! ✨
```

EnvWizard will:
1. Detect your frameworks (Django, PostgreSQL, etc.)
2. Create a virtual environment
3. Install all dependencies
4. Generate .env and .env.example files
5. Add .env to .gitignore

### Usage Examples

#### Detect Project Type
```bash
envwizard detect
```

#### Create Virtual Environment Only
```bash
envwizard create-venv --name venv --python-version 3.11
```

#### Generate .env Files Only
```bash
envwizard create-dotenv
```

#### Custom Setup
```bash
# Skip dependency installation
envwizard init --no-install

# Skip .env generation
envwizard init --no-dotenv

# Custom virtual environment name
envwizard init --venv-name myenv

# Specific Python version
envwizard init --python-version 3.11
```

## 📋 Supported Frameworks

EnvWizard automatically detects and configures:

### Web Frameworks
- Django
- FastAPI
- Flask
- Streamlit

### Databases
- PostgreSQL
- MySQL
- MongoDB
- Redis
- SQLite

### Tools & Libraries
- Celery (Task queues)
- SQLAlchemy (ORM)
- Pandas (Data analysis)
- NumPy (Scientific computing)
- Pytest (Testing)

## 📖 CLI Commands

### `envwizard init`
Complete project setup - creates venv, installs deps, generates .env

**Options:**
- `--path, -p` - Project directory (default: current)
- `--venv-name, -n` - Virtual environment name (default: venv)
- `--python-version` - Python version (e.g., 3.11)
- `--no-install` - Skip dependency installation
- `--no-dotenv` - Skip .env generation

### `envwizard detect`
Analyze project and show detected frameworks

### `envwizard create-venv`
Create virtual environment only

### `envwizard create-dotenv`
Generate .env files only

### `envwizard --version`
Show version information

### `envwizard --help`
Show help message

## 💡 Use Cases

### Starting a New Project
```bash
mkdir my-fastapi-app
cd my-fastapi-app
echo "fastapi>=0.100.0" > requirements.txt
envwizard init
```

### Joining an Existing Project
```bash
git clone https://github.com/username/django-project.git
cd django-project
envwizard init
```

## 🔒 Security Features

- ✅ **Input Validation** - All inputs sanitized to prevent command injection
- ✅ **Path Protection** - Prevents path traversal to system directories
- ✅ **Secure Permissions** - .env files created with 0600 (owner-only)
- ✅ **Auto .gitignore** - Automatically adds .env to .gitignore
- ✅ **No Secret Storage** - Generates placeholder values only

## 📊 Performance

| Task | Manual | EnvWizard | Time Saved |
|------|--------|-----------|------------|
| Create venv | 30s | Auto | 30s |
| Install deps | 1-2 min | Auto | 60-120s |
| Create .env | 5-10 min | Auto | 5-10 min |
| Research variables | 5-15 min | Auto | 5-15 min |
| **Total** | **14-31 min** | **~30s** | **95% faster** |

## 🤝 Contributing

Contributions are welcome!

```bash
git clone https://github.com/0xV8/envwizard.git
cd envwizard
pip install -e ".[dev]"
pytest tests/
```

## 📝 Requirements

- Python 3.9+
- pip
- Git (optional)

## 📄 License

MIT License - see LICENSE file for details

## 📧 Support

- 🐛 [Report bugs](https://github.com/0xV8/envwizard/issues)
- 💡 [Request features](https://github.com/0xV8/envwizard/issues)
- ⭐ [Star on GitHub](https://github.com/0xV8/envwizard)

---

**Made with ❤️ for Python developers**

Save hours of setup time. Focus on building great applications.

`pip install envwizard` and get started in seconds! 🚀
