# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a demo project showcasing **Bauplan's data engineering capabilities** for building ETL pipelines using the **Write-Audit-Publish (WAP) pattern**. The project demonstrates a realistic scenario for Intella's telemetry data processing.

### Key Technologies
- **Bauplan**: Core data engineering framework for ETL pipelines (`bauplan>=0.0.3a509`)
- **Python 3.12+**: Minimum required version (strictly enforced)
- **uv**: Modern Python package and project manager (replaces pip/virtualenv)
- **just**: Command runner for development tasks (replaces make)
- **ruff**: Ultra-fast Python linter and formatter (replaces flake8, black, isort)
- **mypy**: Static type checker in strict mode
- **prek**: Modern pre-commit hook manager

## Python Tooling Architecture

### UV Package Management
This project uses **uv** instead of traditional pip/virtualenv workflow:
- **No manual virtualenv needed**: uv manages environments automatically
- **Faster**: Written in Rust, significantly faster than pip
- **Consistent environments**: All commands run via `uv run --env-file .env --`
- **Lock file support**: Ensures reproducible builds

The justfile defines a `UV` alias used by all Python commands:
```justfile
UV := "uv run --env-file .env --"
```

This means every Python tool (pytest, ruff, mypy) runs in a consistent, isolated environment with `.env` variables loaded.

### Dependency Management
Dependencies are defined in `pyproject.toml`:
- **Runtime dependencies**: `[project.dependencies]` - Only Bauplan
- **Dev dependencies**: `[project.optional-dependencies.dev]` - Linters, testing tools
- **Dependency groups**: `[dependency-groups]` - UV-specific groups (e.g., prek)

To add a new dependency:
```bash
# Runtime dependency
uv add package-name

# Dev dependency
uv add --dev package-name
```

## Development Commands

### Initial Setup
```bash
just install  # Install dependencies via uv and setup pre-commit hooks
```

This runs:
1. `uv run --env-file .env -- pip install -e ".[dev]"` - Install package in editable mode
2. `uv run --env-file .env -- pre-commit install` - Setup git hooks

### Daily Development
```bash
just lint     # Run ruff (with auto-fix + unsafe fixes) and mypy
just test     # Run pytest with coverage
just check    # Run all checks (lint + test)
```

### Testing Variations
```bash
just test                                                  # Run all tests with coverage
just test-verbose                                          # Verbose output
uv run --env-file .env -- pytest tests/test_version.py     # Run specific test file
uv run --env-file .env -- pytest -k test_version           # Run tests matching pattern
uv run --env-file .env -- pytest --cov-report=html         # Generate HTML coverage report
```

Coverage reports are generated in:
- **Terminal**: Shows missing lines
- **HTML**: `htmlcov/index.html`
- **XML**: `coverage.xml` (for CI/CD)

### Other Commands
```bash
just clean          # Remove all generated files and caches (.pytest_cache, .mypy_cache, etc.)
just pre-commit     # Run pre-commit hooks manually on all files
just update-hooks   # Update pre-commit hook versions
```

### Environment Management
The project uses `uv` with `.env` file for environment variables:
- **`.env`** - Local environment variables (gitignored, created on init)
- **`.env.example`** - Template showing required variables
- All commands automatically load `.env` via the `UV` alias in justfile
- Ensures consistent environment across all team members

## Code Quality Standards

### Ruff Linting & Formatting
Ruff replaces multiple tools (flake8, black, isort, pyupgrade) with a single fast tool:

**Configuration** (pyproject.toml:31-56):
- Line length: **100 characters**
- Target: **Python 3.12**
- Quote style: **double quotes**
- Indentation: **spaces**

**Enabled rule sets**:
- `E`, `W` - pycodestyle (PEP 8 compliance)
- `F` - pyflakes (logical errors)
- `I` - isort (import sorting)
- `N` - pep8-naming (naming conventions)
- `UP` - pyupgrade (modern Python syntax)
- `B` - flake8-bugbear (common bugs)
- `C4` - flake8-comprehensions (better comprehensions)
- `SIM` - flake8-simplify (simplification suggestions)
- `RUF` - ruff-specific rules

**Per-file ignores**:
- `__init__.py`: Allow unused imports (F401)
- `tests/**/*.py`: Allow assert statements (S101)

**Auto-fix behavior**: `just lint` runs with `--fix --unsafe-fixes` to automatically fix issues

### Type Checking (mypy)
**Strict mode enabled** - All code must be fully typed:

**Required**:
- All functions must have parameter and return type annotations
- No implicit `Optional` types
- No untyped definitions (`disallow_untyped_defs = true`)
- No generic `Any` types (`disallow_any_generics = true`)

**Warnings enabled**:
- `warn_return_any` - Warn if returning Any
- `warn_unused_configs` - Catch config errors
- `warn_redundant_casts` - Unnecessary casts
- `warn_unused_ignores` - Unnecessary `# type: ignore`
- `warn_no_return` - Missing return statements

**Special handling**:
- Bauplan imports ignore missing type stubs (`ignore_missing_imports = true`)

**Example of properly typed code**:
```python
def process_telemetry(data: dict[str, int], threshold: float) -> list[str]:
    """Process telemetry data above threshold."""
    return [k for k, v in data.items() if v > threshold]
```

### Testing (pytest)
**Configuration** (pyproject.toml:76-103):
- Test path: `tests/`
- Naming: `test_*.py`, `Test*` classes, `test_*` functions
- **Branch coverage enabled** - Measures both line and branch coverage
- Minimum coverage target enforced via reports

**Coverage exclusions**:
- `pragma: no cover` - Explicit skip
- `__repr__`, `__main__` blocks
- Abstract methods, NotImplementedError
- TYPE_CHECKING blocks

**Pytest strict mode**:
- `--strict-markers` - Only registered markers allowed
- `--strict-config` - Fail on config errors
- Coverage tracked for `case_study_telemetry` package only

## Project Structure

```
case_study_telemetry/    # Main package for Bauplan pipelines
tests/                   # Test suite
```

### Package Organization
- `case_study_telemetry/` contains the main ETL pipeline code
- `case_study_telemetry/py.typed` marks the package as type-aware (PEP 561)
- Import example: `from case_study_telemetry import __version__`

## Architecture Notes

### WAP Pattern (Write-Audit-Publish)
This project implements the Write-Audit-Publish pattern for data quality:
1. **Write**: Data is written to a staging area
2. **Audit**: Data quality checks are performed
3. **Publish**: Only validated data is promoted to production

When implementing pipelines, ensure all three phases are clearly separated and auditable.

### Bauplan Integration
- Bauplan is the core dependency for data pipeline orchestration
- Type stubs for Bauplan are ignored in mypy configuration
- Future pipeline implementations should follow Bauplan's conventions

## Pre-commit Hooks (prek)

Uses **prek** (modern pre-commit manager) via `.pre-commit-config.yaml`.

**Hooks run automatically on commit**:

1. **Standard checks** (pre-commit-hooks):
   - Trailing whitespace removal
   - End-of-file fixer (ensures newline at EOF)
   - YAML/JSON/TOML validation
   - Merge conflict detection
   - Large file detection (prevents accidental commits)
   - Private key detection (security)

2. **Ruff** (astral-sh/ruff-pre-commit):
   - Linting with auto-fix: `ruff check --fix --exit-non-zero-on-fix`
   - Formatting: `ruff format`

3. **mypy** (pre-commit/mirrors-mypy):
   - Type checking with `--ignore-missing-imports`

**Hook management**:
```bash
just pre-commit      # Run hooks manually on all files
just update-hooks    # Update hook versions
git commit --no-verify  # Bypass hooks (not recommended)
```

**First-time setup**: Hooks install automatically via `just install`

## Writing New Code

### Adding a New Module
1. Create file in `case_study_telemetry/` with full type annotations
2. Add module to `case_study_telemetry/__init__.py` exports if public API
3. Create corresponding test file in `tests/`
4. Run `just check` to verify linting, types, and tests pass

### Type Annotation Requirements
Every function needs types:
```python
# Good
def extract_metrics(
    raw_data: dict[str, Any],
    filters: list[str] | None = None
) -> pd.DataFrame:
    ...

# Bad - will fail mypy
def extract_metrics(raw_data, filters=None):
    ...
```

### Import Organization
Ruff automatically sorts imports in this order:
1. Standard library
2. Third-party packages (Bauplan, pandas, etc.)
3. Local imports

Example:
```python
import sys
from pathlib import Path

import bauplan
import pandas as pd

from case_study_telemetry.utils import helper
```
