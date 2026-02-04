# Bauplan Pipelines

This directory contains Bauplan data transformation pipelines used by the WAP flow.

## Directory Structure

```
pipelines/
├── README.md                        # This file
└── telemetry_bronze_to_silver/      # Bronze → Silver transformation pipeline
    ├── README.md                    # Pipeline-specific documentation
    ├── bauplan_project.yml          # Bauplan project configuration
    └── models.py                    # Transformation models
```

## Integration with WAP Flow

The Prefect WAP flow (`case_study_telemetry/flows/wap_telemetry_flow.py`) integrates these pipelines via the transformation task:

**Flow execution order:**
1. **Write Phase (Ingestion)**:
   - `ingest_from_s3()` creates `{namespace}.{table}_bronze`

2. **Write Phase (Transformation)**:
   - `run_transformations()` calls `client.run()` on the pipeline
   - Pipeline reads from `{namespace}.{table}_bronze`
   - Pipeline outputs to `{namespace}.{table}` (silver)

3. **Audit Phase**:
   - Quality checks run on `{namespace}.{table}` (silver)

4. **Publish Phase**:
   - Merge to main if audits pass

## Pipeline Development Workflow

### 1. Create New Pipeline
```bash
mkdir -p pipelines/my_new_pipeline
cd pipelines/my_new_pipeline

# Create project configuration
cat > bauplan_project.yml <<EOF
project:
  id: $(uuidgen | tr '[:upper:]' '[:lower:]')
  name: my_new_pipeline
EOF

# Create models.py with your transformations
# See telemetry_bronze_to_silver/models.py for examples
```

### 2. Test Pipeline Locally
```bash
# Get your username
bauplan info

# Create dev branch
bauplan branch create <username>.test-pipeline
bauplan branch checkout <username>.test-pipeline

# Dry run (fast, no materialization)
cd pipelines/my_new_pipeline
bauplan run --dry-run

# Full run
bauplan run
```

### 3. Integrate with WAP Flow

Update `case_study_telemetry/tasks/transformation_tasks.py` to call your pipeline:

```python
pipeline_dir = repo_root / "pipelines" / "my_new_pipeline"
run_state = client.run(
    project_dir=str(pipeline_dir),
    ref=branch,
    namespace=namespace,
    parameters={"param1": value1},
)
```

## Pipeline Guidelines

### Model Naming Convention
- **Function name = output table name**
- Example: `def signals()` creates table `{namespace}.signals`
- Be explicit and descriptive (avoid generic names like `output` or `result`)

### Input/Output Schema
- **Always specify `columns` parameter** in `@bauplan.model()` for validation
- **Use I/O pushdown**: Specify `columns` and `filter` in `bauplan.Model()` inputs
- **Document with docstrings**: Include ASCII table showing output schema

### Parameters
- **Declare parameters** in `bauplan_project.yml` before using them
- Use function parameters for runtime configuration (e.g., `min_date`)
- Pass via `parameters` dict in `client.run()`
- Document all parameters in model docstring

Example parameter declaration:
```yaml
# bauplan_project.yml
parameters:
  min_date:
    type: str  # Valid types: bool, int, float, str, vault, secret
    default: "1980-01-01"
    description: "Minimum date for filtering"
```

### Dependencies
- Specify Python version and packages in `@bauplan.python()` decorator
- Import packages **inside** the function, not at module level
- Example: `@bauplan.python("3.12", pip={"polars": "1.15.0"})`

## Troubleshooting

### "Table not found" errors
- Ensure source tables exist before running pipeline
- Check table names match between ingestion and transformation
- Verify namespace is correct

### Pipeline execution fails
- Check logs: `run_state.job_status` will show failure reason
- Verify branch exists and is checked out
- Run with `--dry-run` first to validate DAG

### Output schema mismatch
- Ensure `columns` in `@bauplan.model()` matches actual output
- Check data types are compatible
- Use `bauplan table get` to inspect actual schema

### "Unexpected parameters: X"
- All runtime parameters must be declared in `bauplan_project.yml`
- Add missing parameter with type, default, and description
- Restart the run after updating configuration

## References

- [Bauplan Documentation](https://docs.bauplanlabs.com/)
- [Python SDK Reference](https://docs.bauplanlabs.com/reference/bauplan)
- [Pipeline Skill Guide](.claude/skills/new-pipeline/README.md)
