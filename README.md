# Case Study: Telemetry Data Engineering with Bauplan

> A production-ready demo showcasing modern data engineering practices using Bauplan's Write-Audit-Publish (WAP) pattern for satellite telemetry data processing.

## Overview

This project demonstrates how to build **robust, scalable ETL pipelines** for real-world satellite operations data. Built in collaboration with [Intella](https://www.intella.tech/), it showcases how [Bauplan](https://www.bauplanlabs.com/) enables production-grade data quality and pipeline orchestration for mission-critical telemetry processing.

### About Intella

[Intella](https://www.intella.tech/) is a software company that develops **mission intelligence solutions for satellite operations**. Their flagship product, **Mercury**, addresses a critical challenge in modern space operations: as satellite fleets grow, the volume of telemetry data increases exponentially, making it impossible for operators to manually monitor every signal.

**The Problem Mercury Solves**:
- **Operational Overload**: Satellite operators are drowning in telemetry signals from growing fleets
- **Hidden Risks**: Critical anomalies get lost in the noise of routine monitoring
- **Scaling Bottleneck**: Traditional monitoring doesn't scale—more satellites = proportionally more human effort
- **Delayed Detection**: Manual monitoring means slower response times to satellite health issues

**Why Satellite Operators Choose Intella**:
- 🎯 **Focus on What Matters**: Mercury filters routine noise and highlights only actionable events
- ⚡ **Faster Response**: ML-powered anomaly detection alerts operators before issues become critical
- 📈 **Scale Without Hiring**: Manage growing satellite fleets without proportional increases in operations staff
- 🔗 **Non-Disruptive Integration**: Works alongside existing ground systems—no need to replace infrastructure
- 🧠 **Operational Intelligence**: Transforms raw telemetry into insights operators can act on immediately


### The Telemetry Data Challenge

**What is satellite telemetry?** Telemetry is data transmitted from satellites to ground stations during antenna passages (communication windows). This data includes:
- **Sensor readings** from onboard instruments (temperature, voltage, orientation, etc.)
- **Health status** indicators (battery levels, communication health, subsystem status)
- **Environmental conditions** (radiation levels, thermal conditions, solar panel performance)

**The data hierarchy**:
- **Sensors** → Individual measurement points (e.g., battery voltage sensor)
- **Units** → Collections of related sensors (e.g., power subsystem with multiple voltage/current sensors)
- **Satellite** → Complete spacecraft composed of multiple units

**The processing challenge**: Raw telemetry data arriving at ground stations is **not ready for immediate use**. It requires:
1. **Cleaning** - Remove corrupt or incomplete transmissions
2. **Standardization** - Normalize timestamps, units, and formats across different sensors
3. **Deduplication** - Handle redundant transmissions from overlapping antenna passes
4. **Validation** - Ensure data quality before feeding downstream ML models

This pipeline demonstrates a **realistic ETL scenario** that processes telemetry data through the complete Write-Audit-Publish workflow, ensuring only validated, high-quality data reaches Intella's ML models and analytics systems.

### Why This Project?

This case study addresses **real-world satellite operations challenges** while showcasing **AI-assisted development workflows**:

- 🛰️ **Real Domain Expertise** - Built with input from actual satellite operators (Intella)
- 📡 **Production Data Patterns** - Handles real telemetry characteristics (duplicates, format inconsistencies, quality issues)
- 🔒 **Mission-Critical Requirements** - Implements safety patterns (WAP) required when data quality directly impacts satellite   operations
- 🎯 **End-to-End Pipeline** - Complete workflow from raw S3 data to ML-ready datasets
- ⚡ **Modern Stack** - Demonstrates best practices with cutting-edge tools (Bauplan, uv, ruff, ty)
- 🤖 **AI-Native Development** - Built-in Claude Code integration with Skills for 10x faster pipeline creation

**Perfect for**:
- 🎓 **Data engineers** learning production patterns and AI-assisted development
- 🔍 **Teams evaluating Bauplan** for their data lakehouse needs
- 🚀 **Organizations exploring Claude Code** for accelerating data pipeline development
- 🛰️ **Space industry professionals** interested in modern telemetry processing workflows

### Why Bauplan?

**[Bauplan](https://www.bauplanlabs.com/)** is a next-generation data lakehouse platform that makes building production-grade data pipelines dramatically simpler and safer.

**Traditional Data Engineering Challenges**:
- **Complex orchestration** setup (Airflow, Dagster) with steep learning curves
- **Manual data quality checks** scattered across pipelines
- No built-in **staging/validation** workflow—easy to corrupt production data
- **Difficult to test** and iterate on transformations safely
- **Inconsistent environments** between development and production

**How Bauplan Solves These**:
- **Git-Like Branching for Data**: Develop and test on isolated branches, merge only when validated
- **Built-in WAP Pattern**: Native support for Write-Audit-Publish ensures data quality by design
- **Declarative Pipelines**: Define transformations as Python functions—no complex DAG configuration
- **Type-Safe by Default**: Full integration with Python type checking (ty, mypy)
- **Instant Feedback**: `--dry-run` mode for fast iteration without materializing data
- **Reproducible Builds**: Immutable lineage tracking ensures you can always reproduce results

**Claude AI Integration** 🤖:
Bauplan is designed to work seamlessly with AI coding assistants like Claude. This project includes:
- **Skills System**: Pre-built workflows for common tasks (e.g., `/wap` for data ingestion, `/new-pipeline` for scaffolding)
- **AI-Friendly Patterns**: Declarative syntax that's easy for LLMs to understand and generate
- **Automatic Best Practices**: Skills guide Claude to follow WAP patterns and safety rules automatically
- **Rapid Prototyping**: Generate production-quality pipelines in minutes, not hours

**Example**: Creating a new pipeline with Claude:
```bash
# In your Claude Code session, just use a skill:
/new-pipeline

# Claude will:
# 1. Scaffold the complete project structure
# 2. Generate model definitions with proper schemas
# 3. Set up Bauplan configuration files
# 4. Add data quality checks
# 5. Create documentation
```

**Why This Matters for Data Teams**:
- 🚀 **Faster Development**: Skills + AI turn hours of boilerplate into minutes of review
- 🛡️ **Safety by Design**: WAP pattern prevents production data corruption
- 🎓 **Lower Learning Curve**: Declarative syntax is easier to understand and maintain
- 🔄 **Better Iteration**: Branch-based workflow enables safe experimentation

## Use Case: Satellite Telemetry Processing Pipeline

This project implements a **realistic telemetry processing pipeline** that mirrors production workflows at satellite operations companies like Intella. It demonstrates the complete journey from raw satellite data to ML-ready datasets.

### Real-World Scenario

**Context**: A satellite operator receives telemetry data from multiple satellites during antenna passage windows. Each satellite contains numerous units (power, thermal, communication, attitude control), and each unit has multiple sensors generating time-series data.

**Raw Data Characteristics**:
- **Source**: Parquet files stored in S3 (simulating ground station data dumps)
- **Volume**: Multiple files per day, each containing thousands of sensor readings
- **Quality Issues**: Duplicate transmissions, missing timestamps, sensor value anomalies
- **Format Inconsistencies**: Mixed timestamp formats, string-encoded numeric values

### Data Pipeline Stages

#### 1. **Extract (Bronze Layer)**
Ingest raw telemetry data from S3 storage:
- Read Parquet files from ground station data dumps
- Preserve original data structure (no transformations yet)
- Create `signals_bronze` table in Bauplan staging branch

**Data at this stage**:
```
time, dateTime, sensors, value (as string)
2024-01-15T10:23:45Z, 1705318425, battery_voltage, "12.8"
2024-01-15T10:23:45Z, 1705318425, solar_panel_temp, "45.2"
```

#### 2. **Transform (Silver Layer)**
Clean and standardize telemetry into analysis-ready format:
- **Timestamp normalization** - Convert to consistent format
- **Type casting** - String values → numeric (double precision)
- **Column renaming** - `sensors` → `signal` for clarity
- **Deduplication** - Handle overlapping antenna passes (keep highest value per signal/time)
- **Null removal** - Filter incomplete records

**Data after transformation**:
```
time (timestamp), signal (string), value (double), value_original (string)
2024-01-15 10:23:45, battery_voltage, 12.8, "12.8"
2024-01-15 10:23:45, solar_panel_temp, 45.2, "45.2"
```

#### 3. **Load & Validate (WAP Pattern)**
Store processed data with quality guarantees:
- **Write** to staging branch (isolated from production)
- **Audit** with comprehensive quality checks
- **Publish** to main only if validation passes

### Quality Assurance

The WAP pattern implementation includes production-grade validations:

**Data Quality Checks**:
- ✅ **Schema validation** - Ensure expected columns and types
- ✅ **Completeness checks** - No null values in critical fields (time, signal, value)
- ✅ **Range validation** - Numeric values within physically plausible bounds
- ✅ **Uniqueness constraints** - Deduplicated (signal, time) pairs
- ✅ **Row count validation** - Sufficient data volume after cleaning

**Why this matters**: These validations prevent corrupt or incomplete data from reaching:
- ML models that predict satellite anomalies
- Operational dashboards showing real-time health
- Alerting systems for critical events
- Historical analysis and trend detection

### Downstream Impact

Clean, validated telemetry enables Intella's Mercury platform to:
- **Detect anomalies** - ML models identify unusual sensor patterns
- **Generate alerts** - Operators receive actionable notifications
- **Provide insights** - Transform raw signals into operational events
- **Scale operations** - Handle growing satellite fleets without proportional human effort

## Features

**What This Project Demonstrates**:

- 🛰️ **Real-World Data Engineering** - Production patterns for satellite telemetry processing
- 📊 **WAP Pattern Implementation** - Safe data quality assurance with staging branches (zero-downtime deployments)
- 🔄 **Complete ETL Pipeline** - Extract from S3, Transform with Bauplan, Load with validation
- 🤖 **AI-Assisted Development** - Claude Code integration with Skills for 10x faster pipeline creation
- 🎯 **Type-Safe Code** - Full Python type checking (ty) and modern linting (ruff)
- 🚀 **Modern Tooling** - Fast package management (uv), simple commands (just), automated quality checks
- 🐳 **Orchestration Ready** - Prefect integration for scheduling, monitoring, and production workflows
- 🔐 **Production Safety** - Branch-based development, data quality gates, automated validation

## Technology Stack

**Core Platform**:
- **[Bauplan](https://www.bauplanlabs.com/)** - Data lakehouse with built-in WAP pattern support and Git-like branching
- **[Prefect](https://www.prefect.io/)** - Workflow orchestration and monitoring for production deployments

**AI-Assisted Development**:
- **[Claude Code](https://claude.ai/code)** - AI coding assistant with specialized Skills for pipeline generation
- **Skills System** - Pre-built workflows (`/wap`, `/new-pipeline`) for rapid development
- **CLAUDE.md** - Project-specific AI guidance ensuring best practices

**Development Tools**:
- **[Python 3.12+](https://www.python.org/)** - Modern Python with latest type system features
- **[uv](https://github.com/astral-sh/uv)** - Fast package manager replacing pip/virtualenv
- **[just](https://just.systems/)** - Simple command runner for development tasks
- **[ruff](https://docs.astral.sh/ruff/)** - Lightning-fast linter and formatter
- **[ty](https://github.com/astral-sh/ty)** - Fast type checker
- **[pytest](https://docs.pytest.org/)** - Testing framework with coverage reporting

---

# Getting Started

This section covers installation, configuration, and running the pipeline.

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

### 4. Running the WAP Pipeline

The telemetry data pipeline can be run in multiple ways depending on your workflow needs.

#### Option 1: Using Prefect (Orchestrated Workflow)

Run the pipeline with full orchestration, monitoring, and scheduling capabilities:

```bash
# 1. Start all services (PostgreSQL, Prefect Server, Prefect Worker)
just launch

# 2. Deploy the WAP flow to Prefect
just deploy-flow

# 3. Open the Prefect dashboard to monitor and trigger runs
open http://localhost:4200
```

The Prefect dashboard (http://localhost:4200) provides:
- **Flow runs monitoring** - Track execution status and logs
- **Manual triggers** - Run the pipeline on-demand
- **Scheduling** - Set up automated runs
- **Execution history** - Review past runs and debug failures

To view logs:
```bash
just logs              # View all service logs
just logs-service prefect-worker  # View only worker logs
```

To stop services:
```bash
just stop              # Stop all Docker Compose services
```

#### Option 2: Local Python Execution

Run the pipeline directly without Prefect orchestration (useful for quick testing):

```bash
# Using just command
just run-flow

# Or directly with uv
uv run --env-file .env -- python -m case_study_telemetry.flows.wap_telemetry_flow
```

This runs the complete WAP pipeline:
1. **Write** - Creates staging branch, ingests data, runs transformations
2. **Audit** - Executes data quality checks
3. **Publish** - Merges to main (if configured) or shows diff

#### Option 3: VSCode Debugging

Debug the pipeline with breakpoints and step-through execution:

1. Open VSCode in the project directory
2. Press `F5` or go to Run → Start Debugging
3. Select **"Python: WAP Telemetry Flow"** from the debug configuration dropdown
4. Set breakpoints in the code as needed
5. The debugger will stop at breakpoints, allowing you to:
   - Inspect variables
   - Step through execution
   - Evaluate expressions
   - Review call stacks

The debug configuration automatically:
- Loads environment variables from `.env`
- Sets `VERBOSITY=DEBUG` for detailed logging
- Configures proper `PYTHONPATH`

#### Configuration

Before running the pipeline, ensure your `.env` file is configured:

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

**Required configuration variables**:

**S3 Data Source**:
- `S3_SOURCE_BUCKET` - Source S3 bucket for telemetry data (e.g., `intella-bauplan-data`)
- `S3_SOURCE_PATH` - Path within the bucket (e.g., `telemetry/raw/`)
- `S3_SOURCE_PATTERN` - File pattern to match (e.g., `*.parquet`)

**AWS Credentials** (required for S3 ingestion simulation):
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_REGION` - AWS region (e.g., `eu-central-1`)

**Bauplan Configuration**:
- `BAUPLAN_NAMESPACE` - Target namespace for tables (e.g., `telemetry`)
- `BAUPLAN_TARGET_TABLE` - Target table name (e.g., `signals`)

**WAP Behavior**:
- `WAP_ON_SUCCESS` - Behavior after successful audit: `inspect` (show diff only) or `merge` (merge to main)
- `WAP_ON_FAILURE` - Behavior after failed audit: `keep` (keep branch for debugging) or `delete` (cleanup)

**Prefect** (for orchestrated runs):
- `PREFECT_API_URL` - Prefect server URL (default: `http://localhost:4200/api`)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - PostgreSQL backend for Prefect

### 5. Building Pipelines with Claude AI

This project is designed to work seamlessly with [Claude Code](https://claude.ai/code), Anthropic's AI coding assistant, for rapid pipeline development.

#### Available Skills

**Skills are AI-powered workflows** that guide Claude to generate production-quality code following best practices. This project includes:

**`/wap` - WAP Ingestion Skill**:
Safely ingest data from S3 using the Write-Audit-Publish pattern.

```bash
# Usage in Claude Code:
/wap

# Claude will:
# - Create a staging branch
# - Ingest files from S3 to bronze table
# - Run data quality checks
# - Guide you through the publish decision
# - Generate complete, production-ready code
```

**`/new-pipeline` - Pipeline Creation Skill**:
Scaffold new Bauplan pipelines with proper structure.

```bash
# Usage in Claude Code:
/new-pipeline

# Claude will:
# - Create project structure (models.py, bauplan_project.yml)
# - Generate model definitions with schemas
# - Add environment declarations
# - Set up parameters and configuration
# - Create documentation and examples
```

#### Why This Approach is Powerful

**Traditional Pipeline Development**:
1. Research Bauplan documentation
2. Manually write boilerplate (project config, models, schemas)
3. Debug configuration errors
4. Add data quality checks
5. Write tests and documentation
⏱️ **Time: Several hours to days**

**With Claude + Skills**:
1. Run `/new-pipeline` skill
2. Review and customize generated code
3. Test with `bauplan run --dry-run`
4. Deploy
⏱️ **Time: Minutes to an hour**

**Benefits**:
- ✅ **No Boilerplate**: Skills handle repetitive setup automatically
- ✅ **Best Practices Built-in**: WAP pattern, type safety, proper schemas enforced by default
- ✅ **Consistency**: All pipelines follow the same patterns
- ✅ **Documentation**: Skills generate README files and inline docs
- ✅ **Safety Rails**: Claude knows to never write directly to `main`, always use branches

#### Example: Adding a New Transformation

```bash
# In Claude Code session:
"I need to add a gold layer that aggregates signals by hour"

# Claude will:
# 1. Create a new pipeline in pipelines/telemetry_silver_to_gold/
# 2. Define aggregation model with proper schema
# 3. Add hourly windowing logic
# 4. Set up parameters (aggregation window, metrics)
# 5. Update documentation
# 6. Guide you to test with --dry-run before deploying
```

#### Getting Started with Skills

1. **Open this project in Claude Code** (VSCode extension or CLI)
2. **Use skills** for common tasks: `/wap`, `/new-pipeline`
3. **Natural language** for custom tasks: "Add a data quality check for nulls"
4. **Review and test** generated code before deployment

Skills are defined in [`.claude/skills/`](.claude/skills/) directory. See [CLAUDE.md](CLAUDE.md) for full guidance on working with Claude in this project.

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

## Resources

### Documentation
- **[Bauplan Documentation](https://docs.bauplanlabs.com/)** - Data lakehouse platform guides and API reference
- **[Intella](https://www.intella.tech/)** - Mission intelligence for satellite operations
- **[uv Documentation](https://docs.astral.sh/uv/)** - Fast Python package manager
- **[Ruff Documentation](https://docs.astral.sh/ruff/)** - Lightning-fast linter and formatter
- **[Prefect Documentation](https://docs.prefect.io/)** - Workflow orchestration
- **[pytest Documentation](https://docs.pytest.org/)** - Testing framework

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

- **Built with** [Bauplan](https://www.bauplanlabs.com/) - Modern data lakehouse platform
- **Developed in collaboration with** [Intella](https://www.intella.tech/) - Mission intelligence for satellite operations
- **Realistic use case**: Satellite telemetry processing pipeline mirroring production workflows
- **Demo project** showcasing modern data engineering practices for mission-critical data

---

**Questions or Issues?** Open an issue on GitHub or consult [CLAUDE.md](./CLAUDE.md) for AI assistant guidance.
