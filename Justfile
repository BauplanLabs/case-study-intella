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
