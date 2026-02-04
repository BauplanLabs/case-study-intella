# Telemetry Bronze to Silver Pipeline

This Bauplan pipeline transforms raw telemetry data from Bronze schema to Silver schema.

## Pipeline DAG

```
[telemetry.signal_bronze] -> [signal] (Silver)
```

## Transformations

The pipeline transforms all data from bronze to silver:

1. **Column Mapping**: Rename `sensors` -> `signal`
2. **Type Casting**: Parse `value` from string to double
3. **Null Removal**: Remove rows with null time, signal, value, or dateTime
4. **Deduplication**: Keep unique (time, signal) pairs, selecting highest value

### Materialization Strategy

Uses **REPLACE** strategy - the entire silver table is overwritten on each run.

> **Note**: This processes all data from bronze on every run. Partition-based incremental updates will be implemented in a future version for better performance.

## Input Schema (Bronze)

| Column   | Type      | Description              |
| -------- | --------- | ------------------------ |
| time     | Int64     | Unix timestamp           |
| dateTime | Timestamp | Datetime for filtering   |
| sensors  | String    | Sensor identifier        |
| value    | String    | Raw value (unparsed)     |

## Output Schema (Silver)

| Column         | Type      | Description                    |
| -------------- | --------- | ------------------------------ |
| dateTime       | Timestamp | Event timestamp                |
| signal         | String    | Signal identifier (ex-sensors) |
| value          | Float     | Parsed numeric value           |
| value_original | Float     | Copy of parsed value           |

## Parameters

No parameters are currently defined for this pipeline. All data from the bronze table is processed.

## Running the Pipeline

### Local Testing (Dry Run)
```bash
cd pipelines/telemetry_bronze_to_silver
bauplan run --dry-run --ref <your-branch>
```

### Execute Pipeline
```bash
bauplan run --ref <your-branch> --namespace bauplan
```


## Integration

This pipeline is called by the Prefect WAP flow in:
- `case_study_telemetry/tasks/transformation_tasks.py:run_transformations()`

The task uses `client.run()` to execute this pipeline as part of the Write phase.
