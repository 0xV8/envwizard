# envwizard - Complete Setup Guide for PyPI Release

This guide will walk you through setting up and publishing **envwizard** to PyPI.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Testing Locally](#testing-locally)
4. [Publishing to TestPyPI](#publishing-to-testpypi)
5. [Publishing to PyPI](#publishing-to-pypi)
6. [Post-Publication](#post-publication)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
1. **PyPI Account**: Register at https://pypi.org/account/register/
2. **TestPyPI Account**: Register at https://test.pypi.org/account/register/
3. **GitHub Account**: For repository hosting and CI/CD

### Required Software
```bash
# Python 3.8 or higher
python --version

# pip (latest version)
pip --version

# Git
git --version
```

---

## Initial Setup

### 1. Create GitHub Repository

```bash
cd /Users/vipin/Downloads/Opensource/envwizard

# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: envwizard v0.1.0"

# Create GitHub repository (via GitHub CLI or web interface)
gh repo create envwizard --public --source=. --remote=origin

# Push to GitHub
git push -u origin main
```

### 2. Set Up PyPI API Tokens

#### For PyPI:
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `envwizard-publish`
4. Scope: "Entire account" or "Project: envwizard" (after first upload)
5. Copy the token (starts with `pypi-`)

#### For TestPyPI:
1. Go to https://test.pypi.org/manage/account/token/
2. Follow the same steps as above
3. Copy the token

#### Store Tokens Securely:
```bash
# Create .pypirc file (for local publishing)
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PYPI-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
EOF

chmod 600 ~/.pypirc
```

### 3. Configure GitHub Secrets

For automated publishing via GitHub Actions:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `PYPI_API_TOKEN`: Your PyPI token
   - `TEST_PYPI_API_TOKEN`: Your TestPyPI token

---

## Testing Locally

### 1. Set Up Development Environment

```bash
cd /Users/vipin/Downloads/Opensource/envwizard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=envwizard --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

### 3. Check Code Quality

```bash
# Format code
black src/envwizard tests

# Lint code
ruff check src/envwizard tests

# Type checking
mypy src/envwizard
```

### 4. Test CLI Locally

```bash
# Install in editable mode
pip install -e .

# Test commands
envwizard --version
envwizard --help
envwizard detect

# Create a test project and try init
mkdir /tmp/test_project
cd /tmp/test_project
echo "django>=4.0.0" > requirements.txt
envwizard init
```

---

## Publishing to TestPyPI

**Always test on TestPyPI first!**

### 1. Build the Package

```bash
cd /Users/vipin/Downloads/Opensource/envwizard

# Clean previous builds
make clean
# or manually:
rm -rf build/ dist/ *.egg-info

# Build package
python -m build
```

### 2. Check the Build

```bash
# Install twine if not already installed
pip install twine

# Check the distribution
twine check dist/*
```

### 3. Upload to TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Or using make
make publish-test
```

### 4. Test Installation from TestPyPI

```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ envwizard

# Test the installation
envwizard --version
envwizard --help

# Try it on a test project
mkdir /tmp/test_envwizard
cd /tmp/test_envwizard
echo "fastapi>=0.95.0" > requirements.txt
envwizard init
```

---

## Publishing to PyPI

### Method 1: Manual Publishing

```bash
cd /Users/vipin/Downloads/Opensource/envwizard

# Ensure you're on main branch with latest code
git checkout main
git pull origin main

# Clean and build
make clean
make build

# Check the build
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Or using make
make publish
```

### Method 2: Automated Publishing (Recommended)

This uses GitHub Actions to automatically publish when you create a release.

```bash
# 1. Ensure all changes are committed
git add .
git commit -m "Prepare for v0.1.0 release"
git push origin main

# 2. Create and push a tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# 3. Create a GitHub Release
# Go to: https://github.com/YOUR_USERNAME/envwizard/releases/new
# - Select tag: v0.1.0
# - Title: v0.1.0
# - Description: Copy from CHANGELOG.md
# - Click "Publish release"

# GitHub Actions will automatically:
# - Run tests
# - Build package
# - Publish to PyPI
```

---

## Post-Publication

### 1. Verify PyPI Publication

```bash
# Check on PyPI
open https://pypi.org/project/envwizard/

# Install from PyPI
pip install envwizard

# Test installation
envwizard --version
```

### 2. Update Repository Badges

Edit README.md to update the PyPI badge URL:
```markdown
[![PyPI version](https://badge.fury.io/py/envwizard.svg)](https://badge.fury.io/py/envwizard)
```

### 3. Announce the Release

- Create a blog post or announcement
- Share on social media
- Post in relevant Python communities
- Update documentation site (if any)

### 4. Monitor Issues

- Watch GitHub issues for bug reports
- Monitor PyPI download statistics
- Respond to community feedback

---

## Troubleshooting

### Issue: Import errors after installation

**Solution**: Ensure package structure is correct:
```bash
# Check package contents
python -m tarfile --list dist/envwizard-0.1.0.tar.gz
```

### Issue: "File already exists" error on PyPI

**Solution**: You cannot re-upload the same version. Either:
1. Increment version number
2. Delete the files from dist/ and rebuild

### Issue: Tests fail in CI but pass locally

**Solution**:
```bash
# Run tests exactly as CI does
python -m pytest

# Check Python version
python --version
```

### Issue: Module not found errors

**Solution**: Check package structure:
```python
# Ensure __init__.py files exist
find src/envwizard -name "__init__.py"
```

### Issue: CLI command not found after install

**Solution**: Check entry point in pyproject.toml:
```toml
[project.scripts]
envwizard = "envwizard.cli.main:cli"
```

---

## Quick Reference Commands

```bash
# Development workflow
make install-dev          # Install with dev dependencies
make test                 # Run tests
make test-cov            # Run tests with coverage
make format              # Format code
make lint                # Check code quality

# Publishing workflow
make clean               # Clean build artifacts
make build               # Build package
make publish-test        # Publish to TestPyPI
make publish             # Publish to PyPI

# Git workflow
git add .
git commit -m "Your message"
git push origin main
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

---

## Next Steps

After successful publication:

1. **Monitor the project**:
   - Check PyPI download stats
   - Respond to GitHub issues
   - Review pull requests

2. **Plan future releases**:
   - Review feature requests
   - Plan roadmap
   - Update CHANGELOG.md

3. **Engage with community**:
   - Write blog posts
   - Create tutorials
   - Speak at meetups

4. **Continuous improvement**:
   - Add more framework support
   - Improve documentation
   - Optimize performance

---

## Support

If you encounter issues:
- Check existing GitHub issues
- Read the documentation
- Ask in GitHub Discussions
- Contact maintainers

Good luck with your PyPI release! 🚀
