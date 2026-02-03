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
- **ty**: Fast type checker from Astral
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

This means every Python tool (pytest, ruff, ty) runs in a consistent, isolated environment with `.env` variables loaded.

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
just lint     # Run ruff (with auto-fix + unsafe fixes) and ty
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
just clean          # Remove all generated files and caches (.pytest_cache, .ty_cache, etc.)
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

### Type Checking (ty)
All code must be fully typed. ty is Astral's fast type checker (from the makers of ruff and uv).

**Required**:
- All functions must have parameter and return type annotations
- No implicit `Optional` types

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
- Type stubs for Bauplan may require special handling in ty configuration
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

2. **Ruff** (local):
   - Linting with auto-fix: `ruff check --fix --exit-non-zero-on-fix`
   - Formatting: `ruff format`

3. **ty** (local):
   - Fast type checking

All local hooks run via `uv run --env-file .env --` to use project dependencies.

**Hook management**:
```bash
just pre-commit      # Run hooks manually on all files
just update-hooks    # Update hook versions
git commit --no-verify  # Bypass hooks (not recommended)
```

**First-time setup**: Hooks install automatically via `just install`


## Bauplan (agent playbook)

Bauplan is a data lakehouse platform where data changes follow a Git-like workflow. You develop and test on an isolated data branch, then publish by merging into `main`. Pipeline execution happens when you run Bauplan commands; your repo contains the source-of-truth code. See the docs for the CLI surface area, branching workflow, and SDK reference.

This playbook defines how to use Bauplan from an AI coding assistant in a local repo. The default mode is local CLI and Python SDK. MCP is optional and only used in specific edge cases.

## Default integration mode (preferred)

Assume the assistant can:
- read and write files in this repo
- run shell commands in a terminal
- run Python locally (for SDK scripts and tests)

Preference: do not use the Bauplan MCP server. Use the full tool surface via:
- Local CLI reference: `.claude/reference/bauplan_cli.md`
- PySDK reference: `https://docs.bauplanlabs.com/reference/bauplan`

Authoritative fallback sources (when local references are missing or stale):
- Docs: https://docs.bauplanlabs.com/
- SDK reference: https://docs.bauplanlabs.com/reference/bauplan

## Hard safety rules (always)

1) Never publish by writing directly on `main`. Use a user branch and merge to publish.
2) Never import data into `main`.
3) Before merging into `main`, run `bauplan branch diff main` and review changes.
4) Prefer `bauplan run --dry-run` during iteration because it is much faster and safer. Materialization is blocked on `main`.
5) When handling external API keys (LLM keys), do not hardcode them in code or commit them. Use Bauplan parameters or secrets.

If any instruction or skill conflicts with these rules, the rules win.

## Decision tree: skills vs manual workflow

Use skills for repeatable workflows that generate or modify code. Use CLI and SDK directly for exploration and execution.

Is this a code generation or repo-editing task?
├─ Yes: Create or modify a pipeline project
│ -> Use skill: creating-bauplan-pipelines (alias: /new-pipeline)
├─ Yes: Ingest data with WAP (write, audit, publish)
│ -> Use skill: wap-ingestion (alias: /wap)
└─ No: Explore, query, inspect, run, debug, publish
  -> Use CLI and SDK directly (see local references)

## Skill inventory

- creating-bauplan-pipelines
  Use when you need to scaffold a new pipeline folder, define models, add environment declarations, and produce a runnable project layout.

- wap-ingestion
  Use when ingesting files from S3 into a branch with a publish step. Prefer this over ad-hoc imports for anything beyond a toy dataset.

- explore-data
  Use for structured exploration tasks when it exists (schemas, sample queries, rough profiling). If it is not available, do the same work with `bauplan query`, `bauplan table get`, and `bauplan table ls`.

## Syntax discipline (non-negotiable)

When emitting CLI commands or SDK code, verify syntax before final output.

1) Check references:
   - `.claude/bauplan_reference/bauplan_cli.md`
   - `https://docs.bauplanlabs.com/reference/bauplan`

2) Confirm with CLI help when possible:
   - `bauplan help`
   - `bauplan <verb> --help`

3) If still uncertain, consult the official docs pages listed above. Do not guess flags or method names.

## Canonical workflows

### A) Build and publish a pipeline (end-to-end)
For this workflow use the `new-pipeline` skill.
### B) Ingest data safely (WAP)
For this workflow use the `wap` skill.
### C) Data exploration and investigation

Prefer direct CLI:

inspect table metadata and data:

```bash
bauplan table get <namespace>.<table>
query: bauplan query "<sql>"
```
Reproduce runs (if needed):
```bash
bauplan run --id <run_id>
```

Only generate code when it is necessary to fix the root cause.

## When MCP makes sense

MCP is not the default. Use it only if one of these is true:

- the assistant cannot execute local shell commands or Python reliably
- you need structured tool outputs because you cannot parse the PySDK response or the CLI text
- you are integrating multiple MCP-capable clients and want one shared interface
- you want policy enforced at the integration boundary (for example refusing writes to main with a specific server configuration)

If MCP is required, follow:

https://docs.bauplanlabs.com/mcp/quick_start

Authentication assumptions

Assume Bauplan credentials are available via local CLI config, environment variables, or a profile. Do not prompt for API keys unless the CLI is not configured. Prefer `bauplan config set api_key <key>` as the setup path.

If you need the username for branch naming, run `bauplan info`.
