# Test Gaps Summary - Quick Reference

## Overall Status
- **Current Coverage:** 58% (440/763 lines)
- **Current Tests:** 50 (all passing)
- **Quality Score:** 6.5/10
- **Production Ready:** NO - Critical gaps exist

## Top 5 Critical Issues

### 1. CLI Module - 0% Coverage ❌ CRITICAL
**Problem:** The primary user interface has ZERO tests
**Impact:** Users may experience broken commands, crashes, incorrect output
**Lines Missing:** 150 (all of cli/main.py)
**Effort:** 2-3 days
**Tests Needed:** ~20

### 2. DependencyDetector - 29% Coverage ❌ CRITICAL
**Problem:** Core dependency parsing is severely undertested
**Impact:** pyproject.toml and Pipfile users have broken functionality
**Lines Missing:** 79/112
**Key Missing:**
- `_parse_pyproject_deps()` - ENTIRELY UNTESTED
- `_parse_pipfile_deps()` - ENTIRELY UNTESTED
- `has_dev_dependencies()` - ENTIRELY UNTESTED
**Effort:** 1-2 days
**Tests Needed:** ~18

### 3. VirtualEnvManager Python Version - 36% Coverage ⚠️ HIGH
**Problem:** Python version selection completely untested
**Impact:** Advertised feature may not work
**Lines Missing:** 32/89
**Key Missing:**
- `_find_python_executable()` - ENTIRELY UNTESTED (lines 155-176)
- Python version venv creation (lines 41-49)
- PowerShell detection (lines 178-182)
**Effort:** 0.5-1 day
**Tests Needed:** ~8

### 4. Cross-Platform Testing - 0% ❌ HIGH
**Problem:** Only tested on macOS
**Impact:** Windows users may have broken activation, wrong paths
**Key Missing:**
- Windows PowerShell vs CMD activation
- Path separator handling
- .exe extension handling
**Effort:** 1-2 days
**Tests Needed:** ~10

### 5. Error Path Coverage - ~15% ❌ HIGH
**Problem:** Exception handlers and error scenarios barely tested
**Impact:** Crashes, poor error messages, data loss on failures
**Key Missing:**
- Subprocess failures
- Permission errors
- Malformed file handling
- Network/timeout errors
**Effort:** 2 days
**Tests Needed:** ~15

## Missing Tests by Module

| Module | Coverage | Missing Lines | Priority | Tests Needed |
|--------|----------|---------------|----------|--------------|
| cli/main.py | 0% | 150 | CRITICAL | 20 |
| detectors/dependency.py | 29% | 79 | CRITICAL | 18 |
| venv.py | 64% | 32 | HIGH | 12 |
| detectors/base.py | 72% | 41 | MEDIUM | 15 |
| detectors/framework.py | 83% | 8 | LOW | 5 |
| generators/dotenv.py | 95% | 8 | LOW | 5 |
| core.py | 95% | 3 | LOW | 3 |

## Quick Win Test Additions

### Can Add Today (1-2 hours each):
1. Test `detect_database()` for MySQL, MongoDB, Redis
2. Test `validate_env_file()` with spaces in variable names
3. Test `_is_sensitive()` with more keywords
4. Test `parse_requirements()` with -e and pip options
5. Test error path when venv creation fails

### Can Add This Week (0.5 day each):
1. Test CLI `--version` flag
2. Test CLI `init` command with default options
3. Test `_parse_pyproject_deps()` with simple pyproject.toml
4. Test `_parse_pipfile_deps()` with simple Pipfile
5. Test `has_dev_dependencies()` for requirements-dev.txt

## Recommended Test File to Create

### tests/test_cli.py (CRITICAL - Missing)
```python
"""Tests for CLI interface."""
import pytest
from click.testing import CliRunner
from envwizard.cli.main import cli

def test_cli_version():
    """Test --version flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert "envwizard version" in result.output

def test_cli_init_default(tmp_path):
    """Test init command with defaults."""
    runner = CliRunner()
    result = runner.invoke(cli, ['init', '--path', str(tmp_path)], input='y\n')
    assert result.exit_code == 0

def test_cli_detect(tmp_path):
    """Test detect command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['detect', '--path', str(tmp_path)])
    assert result.exit_code == 0
```

## Edge Cases to Add

### High Impact Edge Cases:
1. Empty requirements.txt
2. Malformed pyproject.toml (invalid TOML)
3. requirements.txt with only comments
4. Very long file paths (>256 chars)
5. Special characters in .env values
6. Permission denied scenarios
7. Concurrent venv creation
8. Interrupted operations (partial state)

### Platform-Specific Edge Cases:
1. Windows paths with backslashes
2. PowerShell vs CMD on Windows
3. Symlinked Python executables
4. Different path separators

## Security Tests to Add

### Critical Security Tests:
1. Path traversal attack prevention
   ```python
   wizard.create_venv_only("../../../etc/passwd")
   # Should fail or sanitize
   ```

2. Command injection in package names
   ```python
   wizard.install_package(venv_path, "pkg; rm -rf /")
   # Should sanitize or reject
   ```

3. .env file permissions
   ```python
   # .env should be readable only by owner (600)
   ```

## Performance Tests to Add

### Recommended Benchmarks:
1. Parse requirements.txt with 1000+ packages
2. Scan project with 10,000+ files
3. Generate .env with 100+ variables
4. Venv creation time baseline

## Test Infrastructure Improvements

### Add to pyproject.toml:
```toml
[tool.pytest.ini_options]
addopts = "--cov=envwizard --cov-report=term-missing --cov-report=html --cov-branch"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
    "unit: marks unit tests",
    "cli: marks CLI tests",
    "windows: marks Windows-specific tests",
    "unix: marks Unix-specific tests",
]

[tool.coverage.report]
fail_under = 70
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### Install Additional Tools:
```bash
pip install pytest-benchmark pytest-timeout pytest-mock hypothesis
```

## 30-Day Action Plan

### Week 1: Critical CLI Tests
- [ ] Day 1-2: Create tests/test_cli.py with version, help tests
- [ ] Day 3-4: Add CLI init command tests (success/failure)
- [ ] Day 5: Add CLI detect, create-venv, create-dotenv tests
- **Goal: CLI coverage 0% → 60%**

### Week 2: DependencyDetector Completion
- [ ] Day 1: Test _parse_pyproject_deps() with various formats
- [ ] Day 2: Test _parse_pipfile_deps()
- [ ] Day 3: Test has_dev_dependencies() for all formats
- [ ] Day 4: Test edge cases (malformed files, encodings)
- [ ] Day 5: Test error paths and exceptions
- **Goal: DependencyDetector 29% → 80%**

### Week 3: Python Version & Cross-Platform
- [ ] Day 1-2: Test _find_python_executable() logic
- [ ] Day 2-3: Test Python version venv creation
- [ ] Day 4-5: Add Windows-specific tests (mock platform)
- **Goal: VirtualEnvManager 64% → 85%**

### Week 4: Error Paths & Edge Cases
- [ ] Day 1-2: Add subprocess failure tests
- [ ] Day 3: Add permission error tests
- [ ] Day 4: Add malformed file tests
- [ ] Day 5: Add concurrent operation tests
- **Goal: Overall coverage 58% → 75%**

## Coverage Goals

### Immediate (1 month):
- Overall: 58% → 75%
- CLI: 0% → 60%
- DependencyDetector: 29% → 80%
- VirtualEnvManager: 64% → 85%

### Short-term (3 months):
- Overall: 75% → 85%
- All modules: >70%
- Branch coverage: >75%

### Long-term (6 months):
- Overall: 85% → 90%
- All modules: >80%
- Branch coverage: >85%
- Mutation score: >80%

## Test Quality Metrics to Track

1. **Line Coverage:** 58% (target: 85%)
2. **Branch Coverage:** Not measured (target: 80%)
3. **Test Count:** 50 (target: 150)
4. **Average Test Time:** 1.19s (keep under 2s)
5. **Flaky Tests:** 0 (maintain)
6. **Test Isolation:** 100% (maintain)

## Quick Reference: What to Test

### For Every New Feature:
- [ ] Happy path (at least 1 test)
- [ ] Error path (at least 1 test)
- [ ] Edge cases (at least 2 tests)
- [ ] Cross-platform if applicable
- [ ] Performance if applicable

### For Every Bug Fix:
- [ ] Regression test (reproduces bug)
- [ ] Edge case that caused bug
- [ ] Similar scenarios to prevent variants

## Resources

### Testing Best Practices:
- pytest documentation: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/
- Test-Driven Development: Write test before code

### Tools:
- pytest-cov: Coverage plugin
- pytest-benchmark: Performance testing
- pytest-mock: Better mocking
- hypothesis: Property-based testing
- mutmut: Mutation testing

## Questions?

If unsure what to test:
1. Look at coverage report: `pytest --cov=envwizard --cov-report=html`
2. Open htmlcov/index.html in browser
3. Find red (uncovered) lines
4. Write tests that execute those lines
5. Run tests: `pytest -v`
6. Check coverage improved

## Next Steps

1. Read full TEST_QUALITY_AUDIT_REPORT.md
2. Start with CLI tests (highest impact)
3. Add tests daily (even 1-2 tests helps)
4. Run coverage after each addition
5. Aim for +1% coverage per day
6. Review progress weekly

---

Generated: November 2, 2025
See: TEST_QUALITY_AUDIT_REPORT.md for detailed analysis
