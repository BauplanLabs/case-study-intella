# Justfile for case-study-telemetry

# UV command alias for running Python commands with environment
UV := "uv run --env-file .env --"

# Default recipe to display help
default:
    @just --list

# Install dependencies and pre-commit hooks
install:
    {{UV}} uv sync --all-groups
    {{UV}} prek install

# Run linters (ruff and ty)
lint:
    {{UV}} ruff check --fix --unsafe-fixes .
    {{UV}} ruff format .
    {{UV}} ty check .


# Run tests with coverage
test:
    {{UV}} pytest

# Run tests in verbose mode
test-verbose:
    {{UV}} pytest -v

# Run tests with coverage report
test-cov:
    {{UV}} pytest --cov --cov-report=html --cov-report=term

# Run pre-commit hooks on all files
pre-commit:
    {{UV}} prek run

# Clean up generated files
clean:
    rm -rf .pytest_cache
    rm -rf .ty_cache
    rm -rf .ruff_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf dist
    rm -rf build
    rm -rf *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Update pre-commit hooks
update-hooks:
    {{UV}} pre-commit autoupdate

# Run all checks (lint + test)
check: lint test

# ==================== Docker & Prefect ====================

# Build the worker image
build:
    docker compose build

# Start all services (PostgreSQL, Prefect Server, Prefect Worker)
launch:
    docker compose up -d

# Start services and rebuild if needed
launch-build:
    docker compose up -d --build

# Stop all services
stop:
    docker compose down

# View service logs
logs:
    docker compose logs -f

# View specific service logs (e.g., just logs-service prefect-server)
logs-service service:
    docker compose logs -f {{service}}

# Create the process work pool (run once after first launch)
create-pool:
    {{UV}} prefect work-pool create process-pool --type process

# Deploy the WAP flow to Prefect
deploy-flow:
    {{UV}} python scripts/deploy_flow.py

# Run the WAP flow directly (without Prefect server)
run-flow:
    {{UV}} python -m case_study_telemetry.flows.wap_telemetry_flow
