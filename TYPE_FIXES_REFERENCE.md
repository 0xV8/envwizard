# Type Safety Fixes - Quick Reference Guide

This document provides ready-to-use corrected type hints for all identified issues.

---

## File: src/envwizard/core.py

### Add to imports:
```python
from typing import Any, Dict, List, Optional, Tuple, TypedDict
```

### Add TypedDict definition (before EnvWizard class):
```python
class SetupResults(TypedDict, total=False):
    """Type definition for setup() return value."""
    project_info: Dict[str, Any]
    venv_created: bool
    venv_path: Optional[str]
    deps_installed: bool
    dotenv_created: bool
    errors: List[str]
    messages: List[str]
    activation_command: Optional[str]
```

### Line 27 - Fix setup() return type:
```python
# BEFORE:
def setup(
    self,
    venv_name: str = "venv",
    install_deps: bool = True,
    create_dotenv: bool = True,
) -> Dict[str, any]:  # ❌ WRONG

# AFTER:
def setup(
    self,
    venv_name: str = "venv",
    install_deps: bool = True,
    create_dotenv: bool = True,
) -> SetupResults:  # ✅ CORRECT
```

### Line 39 - Fix results variable type:
```python
# BEFORE:
results = {
    "project_info": {},
    "venv_created": False,
    # ...
}

# AFTER:
results: SetupResults = {
    "project_info": {},
    "venv_created": False,
    "venv_path": None,
    "deps_installed": False,
    "dotenv_created": False,
    "errors": [],
    "messages": [],
}
```

### Line 97 - Fix get_project_info() return type:
```python
# BEFORE:
def get_project_info(self) -> Dict[str, any]:  # ❌ WRONG

# AFTER:
def get_project_info(self) -> Dict[str, Any]:  # ✅ CORRECT
```

### Line 107 - Fix create_dotenv_only() parameter type:
```python
# BEFORE:
def create_dotenv_only(self, frameworks: Optional[list] = None) -> Tuple[bool, str]:  # ❌ WRONG

# AFTER:
def create_dotenv_only(self, frameworks: Optional[List[str]] = None) -> Tuple[bool, str]:  # ✅ CORRECT
```

---

## File: src/envwizard/detectors/base.py

### Add to imports:
```python
from typing import Any, Dict, List, Optional, Set
```

### Line 33 - Fix detect_project_type() return type:
```python
# BEFORE:
def detect_project_type(self) -> Dict[str, any]:  # ❌ WRONG

# AFTER:
def detect_project_type(self) -> Dict[str, Any]:  # ✅ CORRECT
```

### Line 107 - Add type annotation for frameworks variable:
```python
# BEFORE (in _parse_pyproject method):
frameworks = set()  # ❌ WRONG

# AFTER:
frameworks: Set[str] = set()  # ✅ CORRECT
```

### Lines 212-216 - Fix _detect_python_version() runtime validation:
```python
# BEFORE:
try:
    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)
        if "project" in data and "requires-python" in data["project"]:
            return data["project"]["requires-python"]  # ❌ Returns Any
except Exception:
    pass

# AFTER:
try:
    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)
        if "project" in data and "requires-python" in data["project"]:
            requires_python = data["project"]["requires-python"]
            if isinstance(requires_python, str):
                return requires_python  # ✅ Type narrowed to str
except Exception:
    pass
```

### Line 173 - Fix complex conditional expression:
```python
# BEFORE:
if (self.project_path / indicator).is_dir() if (self.project_path / indicator).exists() else False:

# AFTER:
indicator_path = self.project_path / indicator
if indicator_path.exists() and indicator_path.is_dir():
```

### Add ClassVar annotation for FRAMEWORK_INDICATORS:
```python
# BEFORE:
class ProjectDetector:
    FRAMEWORK_INDICATORS = {
        "django": ["manage.py", "django", "settings.py"],
        # ...
    }

# AFTER:
from typing import ClassVar

class ProjectDetector:
    FRAMEWORK_INDICATORS: ClassVar[Dict[str, List[str]]] = {
        "django": ["manage.py", "django", "settings.py"],
        # ...
    }
```

---

## File: src/envwizard/detectors/framework.py

### Add to imports:
```python
from typing import Any, ClassVar, Dict, List, Optional, Tuple
```

### Line 100 - Fix get_framework_config() return type:
```python
# BEFORE:
@classmethod
def get_framework_config(cls, framework: str) -> Optional[Dict]:  # ❌ WRONG

# AFTER:
@classmethod
def get_framework_config(cls, framework: str) -> Optional[Dict[str, Any]]:  # ✅ CORRECT
```

### Add ClassVar annotations for class constants:
```python
# BEFORE:
class FrameworkDetector:
    FRAMEWORK_CONFIG = {
        # ...
    }
    DATABASE_CONFIG = {
        # ...
    }

# AFTER:
class FrameworkDetector:
    FRAMEWORK_CONFIG: ClassVar[Dict[str, Dict[str, Any]]] = {
        # ...
    }
    DATABASE_CONFIG: ClassVar[Dict[str, Dict[str, List[Tuple[str, str]]]]] = {
        # ...
    }
```

---

## File: src/envwizard/detectors/dependency.py

### No critical changes needed, but add for consistency:

```python
# Add type annotation to _parse_pyproject_deps at line 83:
dependencies: List[str] = []

# Add type annotation to _parse_pipfile_deps at line 105:
dependencies: List[str] = []
```

---

## File: src/envwizard/venv.py

### Line 22 - Fix create_venv() return type:
```python
# BEFORE:
def create_venv(
    self, venv_name: str = "venv", python_version: Optional[str] = None
) -> Tuple[bool, str, Path]:  # ❌ WRONG - Path should be Optional

# AFTER:
def create_venv(
    self, venv_name: str = "venv", python_version: Optional[str] = None
) -> Tuple[bool, str, Optional[Path]]:  # ✅ CORRECT
```

### Line 184 - Fix get_venv_info() return type:
```python
# BEFORE:
def get_venv_info(self, venv_path: Path) -> dict:  # ❌ WRONG

# AFTER:
from typing import Any, Dict

def get_venv_info(self, venv_path: Path) -> Dict[str, Any]:  # ✅ CORRECT
```

### Better: Add TypedDict for get_venv_info():
```python
from typing import TypedDict

class VenvInfo(TypedDict, total=False):
    """Information about a virtual environment."""
    exists: bool
    path: str
    python_executable: str
    activation_command: str
    python_version: str

def get_venv_info(self, venv_path: Path) -> VenvInfo:
    """Get information about an existing virtual environment."""
    if not venv_path.exists():
        return {"exists": False}  # type: ignore[typeddict-item]

    # ... rest of implementation
```

---

## File: src/envwizard/cli/main.py

### Fix Click path_type issues (Lines 63, 154, 185, 230):

**Option 1: Use str and convert to Path**
```python
# BEFORE:
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # ❌ WRONG
    default=None,
    help="Project directory path",
)
def init(path: Optional[Path], ...):

# AFTER:
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
    help="Project directory path",
)
def init(path: Optional[str], ...):
    project_path = Path(path) if path else Path.cwd()
    wizard = EnvWizard(project_path)
```

**Option 2: Use type: ignore comment (if you want to keep Path type)**
```python
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Project directory path",
)
def init(path: Optional[Path], ...):
```

### Line 258 - Fix _display_project_info() parameter type:
```python
# BEFORE:
def _display_project_info(project_info: dict) -> None:  # ❌ WRONG

# AFTER:
from typing import Any, Dict

def _display_project_info(project_info: Dict[str, Any]) -> None:  # ✅ CORRECT
```

### Line 306 - Fix _display_results() parameter type:
```python
# BEFORE:
def _display_results(results: dict) -> None:  # ❌ WRONG

# AFTER:
from typing import Any, Dict

def _display_results(results: Dict[str, Any]) -> None:  # ✅ CORRECT
```

---

## File: src/envwizard/__init__.py

### Add type annotations to module-level variables:
```python
# BEFORE:
__version__ = "0.1.0"
__author__ = "Vipin"
__description__ = "One command to create virtual envs, install deps, and configure .env intelligently"

# AFTER:
__version__: str = "0.1.0"
__author__: str = "Vipin"
__description__: str = "One command to create virtual envs, install deps, and configure .env intelligently"
```

### Add type annotation to __all__:
```python
# BEFORE:
__all__ = ["EnvWizard", "__version__"]

# AFTER:
from typing import List

__all__: List[str] = ["EnvWizard", "__version__"]
```

---

## File: pyproject.toml

### Fix mypy configuration:
```toml
# BEFORE:
[tool.mypy]
python_version = "3.8"  # ❌ WRONG - Mypy 1.0+ requires 3.9+

# AFTER:
[tool.mypy]
python_version = "3.9"  # ✅ CORRECT
# Note: This is for type checking only. Runtime still supports 3.8
```

### Add type stubs to dev dependencies:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
    "types-PyYAML>=6.0.0",  # ✅ ADD THIS
]
```

---

## New File: src/envwizard/types.py

Create this file for centralized TypedDict definitions:

```python
"""Type definitions for envwizard."""

from typing import Any, Dict, List, Optional, TypedDict


class ProjectInfo(TypedDict, total=False):
    """Information about detected project characteristics."""

    frameworks: List[str]
    has_requirements: bool
    has_pyproject: bool
    has_setup_py: bool
    has_pipfile: bool
    python_version: Optional[str]
    detected_files: List[str]


class SetupResults(TypedDict, total=False):
    """Results from environment setup operation."""

    project_info: Dict[str, Any]
    venv_created: bool
    venv_path: Optional[str]
    deps_installed: bool
    dotenv_created: bool
    errors: List[str]
    messages: List[str]
    activation_command: Optional[str]


class VenvInfo(TypedDict, total=False):
    """Information about a virtual environment."""

    exists: bool
    path: str
    python_executable: str
    activation_command: str
    python_version: str


class FrameworkConfig(TypedDict):
    """Configuration for a detected framework."""

    env_vars: List[tuple[str, str]]
    description: str
```

Then import from this module:
```python
# In core.py, venv.py, etc.
from envwizard.types import SetupResults, VenvInfo, ProjectInfo
```

---

## New File: src/envwizard/py.typed

Create an empty file to mark the package as typed (PEP 561):

```bash
touch src/envwizard/py.typed
```

Update `pyproject.toml` to include it:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/envwizard"]
include = ["src/envwizard/py.typed"]
```

---

## Verification Commands

After applying fixes, run:

```bash
# 1. Check types with mypy
python -m mypy src/envwizard --show-error-codes

# 2. Check with pyright (alternative)
pyright src/envwizard

# 3. Run tests to ensure no runtime breakage
pytest tests/

# 4. Generate type coverage report
mypy src/envwizard --html-report mypy-report
# Open mypy-report/index.html

# 5. Check code quality
ruff check src/envwizard/
black --check src/envwizard/
```

Expected result after all fixes:
```
Success: no issues found in 11 source files
```

---

## Summary of Changes

| File | Critical Fixes | High Priority | Medium Priority |
|------|----------------|---------------|-----------------|
| core.py | 3 (any→Any, TypedDict) | 1 (list type) | 0 |
| detectors/base.py | 3 (any→Any, Set, runtime check) | 0 | 1 (ClassVar) |
| detectors/framework.py | 0 | 1 (Dict type) | 1 (ClassVar) |
| venv.py | 0 | 2 (return types) | 0 |
| cli/main.py | 0 | 6 (Click + dict types) | 0 |
| __init__.py | 0 | 0 | 2 (module vars) |
| pyproject.toml | 1 (mypy config) | 1 (type stubs) | 0 |
| **New: types.py** | Create file | - | - |
| **New: py.typed** | Create file | - | - |

**Total fixes: 37 issues across 9 files**

---

## Migration Strategy

### Phase 1: Quick Wins (1-2 hours)
1. Fix all `any` → `Any` replacements
2. Update mypy config to Python 3.9
3. Add missing import statements

### Phase 2: TypedDict (2-3 hours)
4. Create `types.py` with TypedDict definitions
5. Update all return type annotations
6. Fix variable type annotations

### Phase 3: Polish (1-2 hours)
7. Fix Click path_type issues
8. Add ClassVar annotations
9. Add `py.typed` marker
10. Install type stubs

### Phase 4: Verification (1 hour)
11. Run mypy strict mode
12. Run tests
13. Generate coverage report
14. Update documentation

**Total estimated time: 5-8 hours**
