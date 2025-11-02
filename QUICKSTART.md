# envwizard - Quick Start Guide

## 🚀 From Zero to PyPI in 5 Steps

### Step 1: Create GitHub Repository (5 minutes)

```bash
cd /Users/vipin/Downloads/Opensource/envwizard

# Initialize git
git init
git add .
git commit -m "Initial commit: envwizard v0.1.0"

# Create GitHub repo (replace YOUR_USERNAME)
gh repo create envwizard --public --source=. --remote=origin --description "Smart environment setup tool for Python projects"

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Set Up PyPI Accounts (10 minutes)

1. **Register accounts:**
   - PyPI: https://pypi.org/account/register/
   - TestPyPI: https://test.pypi.org/account/register/

2. **Generate API tokens:**
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - Name: `envwizard-publish`
   - Scope: `Entire account`

3. **Add to GitHub Secrets:**
   - Go to: `github.com/YOUR_USERNAME/envwizard/settings/secrets/actions`
   - Add: `PYPI_API_TOKEN` = your PyPI token
   - Add: `TEST_PYPI_API_TOKEN` = your TestPyPI token

### Step 3: Test Locally (15 minutes)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest --cov=envwizard

# Try the CLI
envwizard --help
envwizard detect

# Test on a sample project
mkdir /tmp/test_project
cd /tmp/test_project
echo "django>=4.0.0" > requirements.txt
envwizard init
```

### Step 4: Test on TestPyPI (10 minutes)

```bash
cd /Users/vipin/Downloads/Opensource/envwizard

# Build package
python -m build

# Check build
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation (in new terminal)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ envwizard
envwizard --version
```

### Step 5: Publish to PyPI (5 minutes)

**Option A: Automatic (Recommended)**
```bash
# Create and push tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Create GitHub Release at:
# https://github.com/YOUR_USERNAME/envwizard/releases/new
# - Select tag: v0.1.0
# - Title: v0.1.0
# - Description: Copy from CHANGELOG.md
# - Publish release

# GitHub Actions will automatically publish to PyPI!
```

**Option B: Manual**
```bash
# Build and upload
make build
make publish

# Or manually
twine upload dist/*
```

---

## ✅ Verification Checklist

After publishing:

- [ ] Package appears on PyPI: https://pypi.org/project/envwizard/
- [ ] Installation works: `pip install envwizard`
- [ ] CLI works: `envwizard --version`
- [ ] GitHub Actions passed
- [ ] README displays correctly on PyPI

---

## 📋 Essential Commands

### Development
```bash
make install-dev    # Install with dev dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make format        # Format code
make lint          # Check code quality
make clean         # Clean build artifacts
```

### Building
```bash
make build         # Build package
make publish-test  # Publish to TestPyPI
make publish       # Publish to PyPI
```

### Git Workflow
```bash
git add .
git commit -m "Your message"
git push origin main
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

---

## 🎯 Post-Launch Tasks

### Day 1
- [ ] Share on Twitter/LinkedIn
- [ ] Post on Reddit (r/Python, r/programming)
- [ ] Submit to Hacker News
- [ ] Update personal website/portfolio

### Week 1
- [ ] Write blog post about the project
- [ ] Create tutorial video
- [ ] Respond to issues/feedback
- [ ] Monitor PyPI download stats

### Month 1
- [ ] Add requested features
- [ ] Improve documentation
- [ ] Create examples repository
- [ ] Plan v0.2.0 features

---

## 🐛 Common Issues & Solutions

### Issue: "Package already exists"
**Solution**: Increment version number in `pyproject.toml` and `src/envwizard/__init__.py`

### Issue: "Module not found" after install
**Solution**: Check package structure with `python -m tarfile --list dist/*.tar.gz`

### Issue: Tests fail in CI
**Solution**: Run `python -m pytest` (same as CI) and check Python version

### Issue: CLI command not found
**Solution**: Reinstall with `pip install -e .` or check entry point in `pyproject.toml`

---

## 📊 Track Success

**PyPI Stats**: https://pypistats.org/packages/envwizard
**GitHub Insights**: https://github.com/YOUR_USERNAME/envwizard/pulse
**Download Badge**: Add to README:
```markdown
[![Downloads](https://pepy.tech/badge/envwizard)](https://pepy.tech/project/envwizard)
```

---

## 🎉 You're Done!

Your package is now live on PyPI! Anyone can install it with:

```bash
pip install envwizard
```

**Share it with the world:**
- Twitter: "Just published envwizard 🧙‍♂️ - Smart environment setup for Python! #Python #OpenSource"
- Reddit: Post in r/Python with a demo GIF
- LinkedIn: Professional announcement with project details
- Dev.to: Write a technical blog post

---

## 📞 Need Help?

- **Documentation**: See SETUP_GUIDE.md for detailed instructions
- **Issues**: Open an issue on GitHub
- **Questions**: Use GitHub Discussions
- **Contact**: [Your contact info]

---

**Remember**: This is just v0.1.0 - iterate based on feedback! 🚀

Good luck with your open source journey! 🎊
