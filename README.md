# Case Study: Telemetry Data Engineering with Bauplan

> A production-ready demo showcasing modern data engineering practices using Bauplan's Write-Audit-Publish (WAP) pattern for telemetry data processing at Intella.

## Overview

This project demonstrates how to build **robust, scalable ETL pipelines** using [Bauplan](https://www.bauplanlabs.com/), a modern data engineering framework. It implements a realistic telemetry data processing scenario for Intella, showcasing best practices in data quality, type safety, and pipeline orchestration.

### What is Bauplan?

Bauplan is a next-generation data engineering platform that enables:
- **Declarative pipeline definitions** - Define data transformations as code
- **Built-in data quality** - Native support for the WAP pattern
- **Type-safe transformations** - Full Python type checking integration
- **Reproducible builds** - Immutable data lineage and versioning

### The Write-Audit-Publish (WAP) Pattern

The WAP pattern ensures data quality through three distinct phases:

1. **Write** - Data is written to a staging area without affecting production
2. **Audit** - Data quality checks validate completeness, accuracy, and consistency
3. **Publish** - Only validated data is atomically promoted to production

This pattern provides:
- ✅ Zero downtime deployments
- ✅ Rollback capabilities
- ✅ Data quality guarantees
- ✅ Clear audit trails

## Features

### Data Engineering
- 🔄 **ETL Pipelines** - Extract, Transform, Load workflows for telemetry data
- 📊 **WAP Pattern Implementation** - Production-grade data quality assurance
- 🔍 **Data Validation** - Comprehensive quality checks at every stage

### Code Quality
- 🎯 **Type Safety** - Full type annotations with ty type checker
- ⚡ **Fast Linting** - Ruff for lightning-fast code quality checks
- 🔒 **Pre-commit Hooks** - Automated quality gates before every commit
- ✅ **High Test Coverage** - Comprehensive pytest suite with branch coverage

### Modern Tooling
- 🚀 **uv Package Manager** - Fast, reliable dependency management
- 🛠️ **just Command Runner** - Simple, consistent development commands
- 📦 **Reproducible Environments** - Lock files and environment isolation

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **uv** - Fast Python package manager
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **just** - Command runner ([installation guide](https://github.com/casey/just#installation))
  ```bash
  # macOS
  brew install just

  # Other platforms: see https://github.com/casey/just#installation
  ```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/case-study-telemetry.git
cd case-study-telemetry

# Install dependencies and set up development environment
just install
```

This will:
- Install all dependencies via `uv`
- Set up pre-commit hooks
- Configure the development environment

### 2. Verify Installation

```bash
# Run all quality checks
just check
```

This runs:
- Ruff linting and formatting (with auto-fix)
- ty type checking
- pytest test suite with coverage

### 3. Development Workflow

#### Daily Commands

```bash
just lint     # Run linters (auto-fixes issues)
just test     # Run tests with coverage
just check    # Run all checks (lint + test)
```

#### Testing

```bash
just test                  # Run all tests
just test-verbose          # Verbose test output
just test-cov              # Generate HTML coverage report (opens htmlcov/index.html)
```

#### Running Specific Tests

```bash
# Run a specific test file
uv run --env-file .env -- pytest tests/test_version.py

# Run tests matching a pattern
uv run --env-file .env -- pytest -k test_telemetry

# Run with verbose output
uv run --env-file .env -- pytest -v
```

#### Maintenance

```bash
just clean          # Remove generated files (.pytest_cache, .ty_cache, etc.)
just pre-commit     # Run pre-commit hooks manually
just update-hooks   # Update pre-commit hook versions
```

## Project Structure

```
case-study-telemetry/
├── case_study_telemetry/       # Main package
│   ├── __init__.py            # Package initialization
│   ├── py.typed               # PEP 561 type marker
│   └── ...                    # Pipeline modules (to be implemented)
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_*.py             # Test modules
├── .github/                   # GitHub configuration (if using CI/CD)
├── pyproject.toml            # Project configuration, dependencies, tool settings
├── justfile                  # Development command recipes
├── .pre-commit-config.yaml   # Pre-commit hook configuration
├── .python-version           # Python version (3.12)
├── .env.example              # Environment variable template
├── .env                      # Local environment variables (gitignored)
├── .gitignore                # Git ignore rules
├── README.md                 # This file
└── CLAUDE.md                 # AI assistant guidance
```

### Key Directories

- **`case_study_telemetry/`** - Main Python package containing Bauplan pipelines
- **`tests/`** - Test suite with pytest tests and fixtures
- Configuration files at root define project behavior and tooling

## Technology Stack

### Core Framework
- **[Bauplan](https://www.bauplanlabs.com/)** (≥0.0.3a509) - Data pipeline orchestration with WAP pattern support

### Development Environment
- **[uv](https://github.com/astral-sh/uv)** - Ultra-fast Python package manager (replaces pip/virtualenv)
  - Automatic environment management
  - Reproducible lock files
  - Environment variable integration via `.env`

### Code Quality Tools
- **[ruff](https://docs.astral.sh/ruff/)** (≥0.8.0) - Lightning-fast linter and formatter
  - Replaces: flake8, black, isort, pyupgrade
  - 100 character line length
  - PEP 8 compliance with modern Python idioms

- **[ty](https://github.com/astral-sh/ty)** (≥0.0.14) - Static type checker from Astral
  - Fast type checking
  - All functions must be typed
  - Catches type errors before runtime

### Testing
- **[pytest](https://docs.pytest.org/)** (≥8.3.0) - Testing framework
- **[pytest-cov](https://pytest-cov.readthedocs.io/)** (≥6.0.0) - Coverage reporting
  - Branch coverage enabled
  - HTML and XML reports
  - Terminal output with missing line numbers

### Development Tools
- **[prek](https://github.com/arrai-innovations/prek)** (≥0.3.1) - Modern pre-commit manager
- **[just](https://just.systems/)** - Command runner (replaces make)

### All Commands Use UV

All Python commands run through `uv run --env-file .env --` ensuring:
- Consistent isolated environments
- Automatic dependency resolution
- Environment variable loading from `.env`
- No manual virtualenv activation needed

## Use Case: Intella Telemetry Processing

This project implements a realistic telemetry data processing pipeline for Intella, demonstrating:

### Data Pipeline Stages

1. **Extract** - Ingest telemetry data from various sources
   - IoT devices, sensors, application logs
   - Multiple data formats (JSON, Parquet, CSV)

2. **Transform** - Process and enrich data
   - Data normalization and type conversion
   - Aggregations and feature engineering
   - Time-series calculations

3. **Load** - Store processed data
   - Write to staging area (WAP: Write phase)
   - Run quality validations (WAP: Audit phase)
   - Promote to production (WAP: Publish phase)

### Quality Assurance

The WAP pattern implementation includes:
- **Schema validation** - Ensure data structure consistency
- **Completeness checks** - Verify required fields present
- **Range validation** - Check values within expected bounds
- **Referential integrity** - Validate relationships between datasets
- **Statistical anomaly detection** - Flag unusual patterns

## Resources

### Documentation
- [Bauplan Documentation](https://docs.bauplanlabs.com/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [ty Documentation](https://github.com/astral-sh/ty)
- [pytest Documentation](https://docs.pytest.org/)

### Related Concepts
- [Write-Audit-Publish Pattern](https://www.databricks.com/blog/2019/08/15/how-to-use-databricks-delta-lake-for-write-audit-publish.html)
- [Data Quality in ETL Pipelines](https://www.montecarlodata.com/blog-data-quality-in-etl-pipelines/)

## Troubleshooting

### Common Issues

**Issue**: `uv: command not found`
```bash
# Solution: Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Issue**: `just: command not found`
```bash
# Solution: Install just
brew install just  # macOS
# Or see: https://github.com/casey/just#installation
```

**Issue**: Pre-commit hooks not running
```bash
# Solution: Reinstall hooks
just install
```

**Issue**: Tests failing with import errors
```bash
# Solution: Reinstall in editable mode
just install
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [Bauplan](https://www.bauplanlabs.com/)
- Developed for Intella telemetry use case
- Demo project showcasing modern data engineering practices

---

**Questions or Issues?** Open an issue on GitHub or consult [CLAUDE.md](./CLAUDE.md) for AI assistant guidance.
