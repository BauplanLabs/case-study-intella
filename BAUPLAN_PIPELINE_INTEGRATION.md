# Bauplan Pipeline Integration

## Overview

The transformation step in the WAP flow has been refactored to use a proper Bauplan pipeline instead of executing DDL SQL commands directly via `client.query()`.

## What Changed

### Before (Incorrect Approach)
The `run_transformations` task attempted to create tables using `CREATE TABLE AS SELECT` (CTAS) syntax:

```python
# ❌ This doesn't work - DDL not supported in client.query()
ctas_sql = f"CREATE OR REPLACE TABLE {target_full} AS {transform_sql}"
client.query(query=ctas_sql, ref=branch)
```

**Problems:**
- Bauplan `client.query()` doesn't support DDL commands
- No proper DAG tracking
- No output schema validation
- Inconsistent with Bauplan best practices

### After (Correct Approach)
Created a proper Bauplan pipeline project in `pipelines/telemetry_bronze_to_silver/`:

```python
# ✅ Run Bauplan pipeline
run_state = client.run(
    project_dir=str(pipeline_dir),
    ref=branch,
    namespace=namespace,
    parameters={"min_date": min_date},
)
```

**Benefits:**
- Proper DAG tracking and execution
- Output schema validation via `columns` parameter
- Runtime parameters support
- Follows Bauplan conventions
- Better observability (job_id, status tracking)

## New File Structure

```
pipelines/
├── README.md                        # Pipeline development guide
└── telemetry_bronze_to_silver/      # Bronze → Silver transformation
    ├── README.md                    # Pipeline-specific docs
    ├── bauplan_project.yml          # Project configuration (UUID, name)
    └── models.py                    # Transformation model
```

## Pipeline Details

### Input/Output
- **Input**: `{namespace}.signals_bronze` (created by ingestion step)
- **Output**: `{namespace}.signals` (silver table, created by pipeline)
- **Namespace**: `telemetry` (default from config)

### Transformation Logic
The pipeline (`models.py`) implements the following transformations using DuckDB:

1. **Time Filtering**: `dateTime >= min_date` parameter
2. **Column Mapping**: `sensors` → `signal`
3. **Type Casting**: `value` (string) → `value` (double)
4. **Null Removal**: Remove rows with null time/signal/value
5. **Deduplication**: Keep unique (signal, time) pairs, selecting highest value

### Model Definition

```python
@bauplan.model(
    columns=["time", "signal", "value", "value_original"],
    materialization_strategy="REPLACE",
)
@bauplan.python("3.12", pip={"duckdb": "1.1.3"})
def signals(
    bronze_data=bauplan.Model(
        "signals_bronze",
        columns=["time", "dateTime", "sensors", "value"],
    ),
    min_date: str = "1980-01-01",
):
    # DuckDB transformation logic
    ...
```

**Key features:**
- Output schema validation via `columns` parameter
- Materialized as Iceberg table (`REPLACE` strategy)
- I/O pushdown: only reads needed columns from bronze
- Runtime parameterization via `min_date`

## Integration Flow

The WAP pipeline now works as follows:

### Phase 1: WRITE
1. **Create Branch**: `create_staging_branch()`
2. **Ingest Bronze**: `ingest_from_s3()` → Creates `signals_bronze`
3. **Transform to Silver**: `run_transformations()` → Runs Bauplan pipeline → Creates `signals`

### Phase 2: AUDIT
- Quality checks run on `signals` table (silver)
- All checks query the materialized table created by the pipeline

### Phase 3: PUBLISH
- Merge to `main` if audits pass
- Clean up branch

## Code Changes

### Modified Files

#### `case_study_telemetry/tasks/transformation_tasks.py`
- Removed DDL SQL execution
- Added `client.run()` call to execute Bauplan pipeline
- Updated to handle `RunState` response
- Added job_id tracking

#### `pyproject.toml`
- Added lint exception for `pipelines/**/models.py` (B008 rule)
- Allows `bauplan.Model()` in function defaults (required pattern)

### New Files

#### `pipelines/telemetry_bronze_to_silver/bauplan_project.yml`
- Project UUID and name
- Parameter declarations (min_date)
- Identifies this as a Bauplan pipeline

#### `pipelines/telemetry_bronze_to_silver/models.py`
- `signals()` model function
- DuckDB-based transformation logic
- Output schema validation
- Runtime parameterization

#### `pipelines/telemetry_bronze_to_silver/README.md`
- Pipeline-specific documentation
- Input/output schemas
- Parameter details
- Usage examples

#### `pipelines/README.md`
- General pipeline development guide
- Integration instructions
- Troubleshooting guide

#### `BAUPLAN_PIPELINE_INTEGRATION.md` (this file)
- High-level overview of changes
- Migration explanation

## Testing

### Local Testing (Without WAP Flow)

```bash
# 1. Get your username
bauplan info

# 2. Create and checkout dev branch
bauplan branch checkout main
bauplan branch create <username>.test-transform
bauplan branch checkout <username>.test-transform

# 3. Ensure bronze table exists
bauplan table get telemetry.signals_bronze

# 4. Test pipeline
cd pipelines/telemetry_bronze_to_silver

# Dry run (fast, no materialization)
bauplan run --dry-run

# Full run
bauplan run

# 5. Verify output
bauplan table get telemetry.signals
bauplan query "SELECT * FROM telemetry.signals LIMIT 5"
```

### Integrated Testing (With WAP Flow)

```bash
# Run the full WAP pipeline
python -m case_study_telemetry.flows.wap_telemetry_flow
```

## Configuration

The pipeline uses the following config values (from `.env`):

```env
BAUPLAN_NAMESPACE=telemetry          # Namespace for tables
BAUPLAN_TARGET_TABLE=signals         # Silver table name (bronze = signals_bronze)
```

## Troubleshooting

### "Pipeline directory not found"
- Ensure `pipelines/telemetry_bronze_to_silver/` exists
- Check path construction in transformation task

### "Table signals_bronze not found"
- Bronze table must be created by ingestion step first
- Verify ingestion completed successfully
- Check namespace is correct

### "Pipeline execution failed"
- Check `run_state.job_status` for details
- Verify branch exists and is checked out
- Run with `--dry-run` first to validate

### Output schema mismatch
- Ensure bronze table has columns: `time`, `dateTime`, `sensors`, `value`
- Check data types are compatible
- Verify DuckDB query produces expected columns

### "Unexpected parameters: X" or "validation error for ProjectManager"
- Parameters must be declared in `bauplan_project.yml` before use
- Add parameter to `parameters` section with correct type and default value
- Valid types: `bool`, `int`, `float`, `str`, `vault`, `secret`
- Example:
  ```yaml
  parameters:
    min_date:
      type: str  # Use 'str' not 'string'
      default: "1980-01-01"
      description: "..."
  ```

## Next Steps

1. **Add Expectations**: Create `expectations.py` for data quality checks within the pipeline
2. **Parameterize Table Names**: Consider making source/target table names runtime parameters
3. **Add More Transformations**: Extend pipeline with additional models if needed
4. **Monitoring**: Add logging and metrics collection for pipeline runs

## References

- [Bauplan Documentation](https://docs.bauplanlabs.com/)
- [Bauplan Python SDK](https://docs.bauplanlabs.com/reference/bauplan)
- [Pipeline Skill Guide](.claude/skills/new-pipeline/README.md)
- [WAP Pattern Overview](README.md)
