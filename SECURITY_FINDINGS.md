# envwizard Security Findings - Quick Reference

**Version**: 0.1.0
**Audit Date**: 2025-11-02
**Total Findings**: 12

---

## HIGH SEVERITY (3 findings)

### SEC-001: Command Injection in Package Installation
- **CVSS**: 7.8 (HIGH)
- **CWE**: CWE-78 (OS Command Injection)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/venv.py`
- **Lines**: 142-146
- **Vulnerable Code**:
  ```python
  result = subprocess.run(
      [str(pip_exe), "install", package],  # package not validated
      capture_output=True,
      text=True,
      check=True,
  )
  ```
- **Attack**: `install_package(venv, "pkg; rm -rf /")`
- **Impact**: Arbitrary command execution on host system
- **Fix Priority**: IMMEDIATE (before v0.1.0 release)

---

### SEC-002: Command Injection via Python Version
- **CVSS**: 7.5 (HIGH)
- **CWE**: CWE-78 (OS Command Injection)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/venv.py`
- **Lines**: 152-176
- **Vulnerable Code**:
  ```python
  def _find_python_executable(self, version: str) -> Optional[str]:
      patterns = [
          f"python{version}",  # No validation
          f"python{version.split('.')[0]}.{version.split('.')[1]}",
      ]
      for pattern in patterns:
          subprocess.run([pattern, "--version"], ...)
  ```
- **Attack**: `create_venv("venv", python_version="3; cat /etc/passwd")`
- **Impact**: Command execution, information disclosure
- **Fix Priority**: IMMEDIATE

---

### SEC-003: Path Traversal in Project Detection
- **CVSS**: 7.3 (HIGH)
- **CWE**: CWE-22 (Path Traversal)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/detectors/base.py`
- **Lines**: 27-29, 46, 69-70, 91
- **Vulnerable Code**:
  ```python
  def __init__(self, project_path: Optional[Path] = None) -> None:
      self.project_path = project_path or Path.cwd()  # No validation

  def _parse_requirements(self, req_file: Path) -> Set[str]:
      content = req_file.read_text()  # Can read any file
  ```
- **Attack**: `EnvWizard(Path("/tmp/../../etc/passwd"))`
- **Impact**: Arbitrary file read, information disclosure
- **Fix Priority**: IMMEDIATE

---

## MEDIUM SEVERITY (5 findings)

### SEC-004: Insecure Default Credentials
- **CVSS**: 6.5 (MEDIUM)
- **CWE**: CWE-798 (Hard-coded Credentials)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/detectors/framework.py`
- **Lines**: 13, 68, 77
- **Vulnerable Code**:
  ```python
  "env_vars": [
      ("SECRET_KEY", "django-insecure-change-this-in-production"),
      ("POSTGRES_PASSWORD", "changeme"),
  ]
  ```
- **Impact**: Production deployments with weak default secrets
- **Fix Priority**: HIGH (v0.2.0)

---

### SEC-005: Path Traversal in .env Generation
- **CVSS**: 6.2 (MEDIUM)
- **CWE**: CWE-22 (Path Traversal)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/generators/dotenv.py`
- **Lines**: 32, 205
- **Vulnerable Code**:
  ```python
  def generate_dotenv(self, frameworks, output_file=".env", ...):
      env_path = self.project_path / output_file  # No validation
      env_path.write_text(env_content)

  def add_to_gitignore(self) -> Tuple[bool, str]:
      gitignore_path = self.project_path / ".gitignore"  # No validation
  ```
- **Attack**: `generate_dotenv([], output_file="../../etc/passwd")`
- **Impact**: Write to arbitrary files
- **Fix Priority**: MEDIUM

---

### SEC-006: Insufficient Input Validation
- **CVSS**: 5.8 (MEDIUM)
- **CWE**: CWE-20 (Improper Input Validation)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/venv.py`
- **Lines**: 156-158
- **Vulnerable Code**:
  ```python
  patterns = [
      f"python{version.split('.')[0]}.{version.split('.')[1]}",  # IndexError if version="3"
  ]
  ```
- **Attack**: `create_venv("venv", python_version="x")`
- **Impact**: Application crash, denial of service
- **Fix Priority**: MEDIUM

---

### SEC-007: Information Disclosure via Defaults
- **CVSS**: 5.5 (MEDIUM)
- **CWE**: CWE-200 (Information Disclosure)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/detectors/framework.py`
- **Lines**: 52, 64-96
- **Vulnerable Code**:
  ```python
  "env_vars": [
      ("CELERY_BROKER_URL", "redis://localhost:6379/0"),  # Reveals infrastructure
      ("POSTGRES_PORT", "5432"),
  ]
  ```
- **Impact**: Exposes infrastructure details to attackers
- **Fix Priority**: LOW-MEDIUM

---

### SEC-008: YAML Unsafe Loading Risk
- **CVSS**: 5.3 (MEDIUM)
- **CWE**: CWE-502 (Deserialization of Untrusted Data)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/detectors/base.py`
- **Line**: 6
- **Issue**: `import yaml` present but not used
- **Risk**: If YAML parsing added without using `safe_load()`
- **Fix**: Remove unused import or ensure `yaml.safe_load()` used
- **Fix Priority**: LOW

---

## LOW SEVERITY (4 findings)

### SEC-009: Missing Subprocess Timeouts
- **CVSS**: 3.5 (LOW)
- **CWE**: CWE-400 (Resource Exhaustion)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/venv.py`
- **Lines**: 43, 107, 116, 142
- **Vulnerable Code**:
  ```python
  subprocess.run(
      [python_executable, "-m", "venv", str(venv_path)],
      check=True,
      capture_output=True,
      # Missing timeout parameter
  )
  ```
- **Impact**: Application can hang indefinitely
- **Fix**: Add `timeout=300` to all subprocess calls
- **Fix Priority**: LOW

---

### SEC-010: Error Information Leakage
- **CVSS**: 3.1 (LOW)
- **CWE**: CWE-209 (Information Exposure Through Error)
- **Files**: Multiple files
- **Lines**: Various exception handlers
- **Vulnerable Code**:
  ```python
  except Exception as e:
      return False, f"Failed to create: {str(e)}"  # Leaks details
  ```
- **Impact**: Internal paths and system info exposed
- **Fix**: Generic error messages to users, detailed logging internally
- **Fix Priority**: LOW

---

### SEC-011: Insecure File Permissions
- **CVSS**: 2.8 (LOW)
- **CWE**: CWE-732 (Incorrect Permission Assignment)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/generators/dotenv.py`
- **Lines**: 52, 58
- **Vulnerable Code**:
  ```python
  env_path.write_text(env_content)  # Default permissions (0644)
  ```
- **Impact**: .env file readable by all users (contains secrets)
- **Fix**: Set permissions to 0600 (owner read/write only)
- **Fix Priority**: LOW

---

### SEC-012: DoS via Unbounded Directory Iteration
- **CVSS**: 2.5 (LOW)
- **CWE**: CWE-400 (Resource Exhaustion)
- **File**: `/Users/vipin/Downloads/Opensource/envwizard/src/envwizard/detectors/base.py`
- **Lines**: 178-182
- **Vulnerable Code**:
  ```python
  for item in self.project_path.iterdir():  # No depth/count limit
      if item.is_dir():
          if (item / indicator).exists():
  ```
- **Impact**: Performance degradation on large filesystems
- **Fix**: Add max depth and file count limits
- **Fix Priority**: LOW

---

## Summary by Severity

| Severity | Count | CVSS Range | Fix Priority |
|----------|-------|------------|--------------|
| HIGH | 3 | 7.3-7.8 | IMMEDIATE |
| MEDIUM | 5 | 5.3-6.5 | v0.2.0 |
| LOW | 4 | 2.5-3.5 | v0.3.0 |
| **Total** | **12** | **2.5-7.8** | - |

---

## Summary by Category

| Category | Count | Severity |
|----------|-------|----------|
| Command Injection | 2 | HIGH |
| Path Traversal | 2 | HIGH, MEDIUM |
| Input Validation | 1 | MEDIUM |
| Hard-coded Credentials | 1 | MEDIUM |
| Information Disclosure | 2 | MEDIUM, LOW |
| Resource Exhaustion | 2 | LOW |
| Deserialization | 1 | MEDIUM |
| File Permissions | 1 | LOW |

---

## Summary by File

| File | Findings | Severity |
|------|----------|----------|
| venv.py | 5 | 2 HIGH, 2 MEDIUM, 1 LOW |
| detectors/base.py | 3 | 1 HIGH, 1 MEDIUM, 1 LOW |
| detectors/framework.py | 2 | 2 MEDIUM |
| generators/dotenv.py | 2 | 1 MEDIUM, 1 LOW |

---

## Critical Code Locations

### Most Vulnerable Functions

1. **`VirtualEnvManager.install_package()`** (venv.py:134-150)
   - SEC-001: Command injection
   - Priority: CRITICAL

2. **`VirtualEnvManager._find_python_executable()`** (venv.py:152-176)
   - SEC-002: Command injection
   - SEC-006: Input validation
   - Priority: CRITICAL

3. **`ProjectDetector.__init__()`** (detectors/base.py:27-31)
   - SEC-003: Path traversal
   - Priority: CRITICAL

4. **`ProjectDetector._parse_requirements()`** (detectors/base.py:87-103)
   - SEC-003: Path traversal
   - Priority: CRITICAL

5. **`FrameworkDetector.FRAMEWORK_CONFIG`** (framework.py:10-59)
   - SEC-004: Weak defaults
   - SEC-007: Info disclosure
   - Priority: HIGH

---

## Attack Surface Analysis

### Entry Points (User-Controlled Input)

1. **CLI Arguments**:
   - `--path` → Path traversal
   - `--venv-name` → Command injection
   - `--python-version` → Command injection
   - `package` parameter → Command injection

2. **API Parameters**:
   - `EnvWizard(project_path=...)` → Path traversal
   - `install_package(package=...)` → Command injection
   - `generate_dotenv(output_file=...)` → Path traversal

3. **File Inputs**:
   - `requirements.txt` → Arbitrary file read
   - `pyproject.toml` → Arbitrary file read
   - `Pipfile` → Arbitrary file read

---

## Exploitation Difficulty

| Finding | Difficulty | Requires |
|---------|------------|----------|
| SEC-001 | EASY | CLI access |
| SEC-002 | EASY | CLI access |
| SEC-003 | EASY | API access |
| SEC-004 | MEDIUM | User error (forgetting to change) |
| SEC-005 | EASY | API access |
| SEC-006 | EASY | CLI access |
| SEC-007 | LOW | File access |
| SEC-008 | N/A | Not currently exploitable |
| SEC-009 | MEDIUM | Network delay |
| SEC-010 | LOW | Error triggering |
| SEC-011 | EASY | File system access |
| SEC-012 | MEDIUM | Large filesystem |

---

## Remediation Status Tracking

| ID | Status | Assigned | Due Date | PR# |
|----|--------|----------|----------|-----|
| SEC-001 | 🔴 Open | - | v0.1.0 | - |
| SEC-002 | 🔴 Open | - | v0.1.0 | - |
| SEC-003 | 🔴 Open | - | v0.1.0 | - |
| SEC-004 | 🔴 Open | - | v0.2.0 | - |
| SEC-005 | 🔴 Open | - | v0.2.0 | - |
| SEC-006 | 🔴 Open | - | v0.2.0 | - |
| SEC-007 | 🔴 Open | - | v0.2.0 | - |
| SEC-008 | 🔴 Open | - | v0.2.0 | - |
| SEC-009 | 🔴 Open | - | v0.3.0 | - |
| SEC-010 | 🔴 Open | - | v0.3.0 | - |
| SEC-011 | 🔴 Open | - | v0.3.0 | - |
| SEC-012 | 🔴 Open | - | v0.3.0 | - |

**Legend**: 🔴 Open | 🟡 In Progress | 🟢 Fixed | ✅ Verified

---

## Testing Checklist

### Security Tests to Add

- [ ] Test command injection in package names
- [ ] Test command injection in Python version
- [ ] Test path traversal in project_path
- [ ] Test path traversal in output_file
- [ ] Test input validation edge cases
- [ ] Test malformed version strings
- [ ] Test large file DoS
- [ ] Test file permission checks
- [ ] Test secret generation randomness
- [ ] Test subprocess timeouts
- [ ] Test error message sanitization

---

## References

- **OWASP Top 10 2021**: https://owasp.org/Top10/
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **CVSS 3.1 Calculator**: https://www.first.org/cvss/calculator/3.1
- **Python Security**: https://python.readthedocs.io/en/stable/library/security_warnings.html
- **Bandit Scanner**: https://bandit.readthedocs.io/

---

**Last Updated**: 2025-11-02
**Next Review**: After implementing HIGH severity fixes
