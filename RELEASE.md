# Release Checklist

This document outlines the process for releasing a new version of envwizard.

## Pre-Release Checklist

### 1. Code Quality
- [ ] All tests pass locally: `pytest`
- [ ] Code coverage is >80%: `pytest --cov=envwizard`
- [ ] Code is formatted: `black src/envwizard tests`
- [ ] Linting passes: `ruff check src/envwizard tests`
- [ ] Type checking passes: `mypy src/envwizard`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`

### 2. Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md is updated with new version
- [ ] All docstrings are current
- [ ] Examples in documentation work
- [ ] CONTRIBUTING.md reflects current process

### 3. Version Updates
- [ ] Update version in `src/envwizard/__init__.py`
- [ ] Update version in `pyproject.toml`
- [ ] Update version in documentation/examples if needed

### 4. Testing
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing on:
  - [ ] Linux (Ubuntu)
  - [ ] macOS
  - [ ] Windows
- [ ] Test with different Python versions:
  - [ ] Python 3.8
  - [ ] Python 3.9
  - [ ] Python 3.10
  - [ ] Python 3.11
  - [ ] Python 3.12
- [ ] Test CLI commands:
  - [ ] `envwizard init`
  - [ ] `envwizard detect`
  - [ ] `envwizard create-venv`
  - [ ] `envwizard create-dotenv`

### 5. CI/CD
- [ ] All GitHub Actions workflows pass
- [ ] Build artifacts are generated successfully
- [ ] Package builds without errors: `python -m build`
- [ ] Package passes twine check: `twine check dist/*`

## Release Process

### 1. Prepare Release Branch
```bash
git checkout -b release/v0.x.0
```

### 2. Update Version Numbers
```python
# src/envwizard/__init__.py
__version__ = "0.x.0"
```

```toml
# pyproject.toml
version = "0.x.0"
```

### 3. Update CHANGELOG.md
```markdown
## [0.x.0] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Changed
- Change 1

### Fixed
- Bug fix 1
```

### 4. Commit Changes
```bash
git add .
git commit -m "Release version 0.x.0"
git push origin release/v0.x.0
```

### 5. Create Pull Request
- Create PR from release branch to main
- Wait for CI to pass
- Get approval from maintainers
- Merge to main

### 6. Create Git Tag
```bash
git checkout main
git pull origin main
git tag -a v0.x.0 -m "Release version 0.x.0"
git push origin v0.x.0
```

### 7. Create GitHub Release
1. Go to GitHub repository → Releases
2. Click "Draft a new release"
3. Select the tag you just created
4. Title: "v0.x.0"
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

### 8. Verify PyPI Publication
- GitHub Action will automatically publish to PyPI
- Verify package appears on PyPI: https://pypi.org/project/envwizard/
- Test installation: `pip install envwizard==0.x.0`

## Post-Release

### 1. Verify Installation
```bash
# In a fresh virtual environment
pip install envwizard
envwizard --version
envwizard init --help
```

### 2. Test Installed Package
```bash
# Create a test project and run envwizard
mkdir test_project
cd test_project
echo "django>=4.0" > requirements.txt
envwizard init
```

### 3. Update Documentation
- [ ] Update badges in README if needed
- [ ] Announce release on relevant channels
- [ ] Update any external documentation

### 4. Prepare for Next Development Cycle
```bash
# Update version to next development version
# src/envwizard/__init__.py
__version__ = "0.x.1-dev"
```

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

### Version Increments

- **Patch Release** (0.1.x → 0.1.y):
  - Bug fixes
  - Documentation updates
  - Performance improvements
  - No new features

- **Minor Release** (0.x.0 → 0.y.0):
  - New features
  - New framework support
  - New CLI commands
  - Backward compatible changes

- **Major Release** (x.0.0 → y.0.0):
  - Breaking API changes
  - Major restructuring
  - Removal of deprecated features

## Hotfix Process

For critical bugs in production:

1. Create hotfix branch from main:
   ```bash
   git checkout -b hotfix/v0.x.y main
   ```

2. Fix the bug and add tests

3. Update version (patch increment)

4. Follow release process steps 3-8

5. Merge hotfix back to develop:
   ```bash
   git checkout develop
   git merge hotfix/v0.x.y
   ```

## Rollback Procedure

If a release has critical issues:

1. **Do not delete the release or tag**
2. **Create a new patch release** with the fix
3. **Mark the problematic version** in CHANGELOG as "YANKED"
4. **Optionally yank from PyPI**:
   ```bash
   pip install twine
   twine upload --skip-existing dist/*
   # Then manually yank on PyPI web interface
   ```

## Communication

After release:
- [ ] Update project homepage/documentation site
- [ ] Post on relevant forums/communities
- [ ] Notify users of breaking changes (if any)
- [ ] Update issue templates if needed

## Metrics to Track

- Download statistics from PyPI
- GitHub stars and forks
- Issue reports after release
- User feedback and feature requests
