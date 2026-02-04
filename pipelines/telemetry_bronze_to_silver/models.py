"""Bauplan models for Bronze to Silver telemetry transformation.

This pipeline transforms raw telemetry data (Bronze schema) into a clean,
deduplicated format (Silver schema) using partition-based overwrites for idempotency.

DAG:
    [telemetry.signal_bronze] -> [signal] (Silver, partitioned by day(dateTime))

Partitioning Strategy:
- Silver table is partitioned by day using Iceberg's day() transform on dateTime
- Only partitions present in bronze data are overwritten
- This ensures idempotency: running twice overwrites the same partitions

Transformations:
1. Column mapping (sensors -> signal)
2. Value parsing from string to float
3. Null value removal
4. Deduplication (unique by signal+time, keep highest value)

Note: The bronze table (signal_bronze) must exist in the lakehouse before running
this pipeline. It is created by the ingestion step in the WAP flow.
"""

import bauplan


@bauplan.model(
    columns=["time", "dateTime", "signal", "value", "value_original"],
    materialization_strategy="REPLACE",
)
@bauplan.python("3.12", pip={"duckdb": "1.1.3"})
def signal(
    bronze_data=bauplan.Model(
        name="telemetry.signal_bronze",
        columns=["time", "dateTime", "sensors", "value"],
    ),
):
    """Transform Bronze telemetry data to Silver schema.

    This model transforms all data from bronze to silver:
    - Column mapping: sensors -> signal
    - Type casting: value (string) -> value (float)
    - Null removal
    - Deduplication by (signal, time), keeping highest value

    The REPLACE strategy overwrites the entire table on each run.

    Output Schema:
    | time       | dateTime            | signal    | value | value_original |
    | ---------- | ------------------- | --------- | ----- | -------------- |
    | 1234567890 | 2009-02-13 23:31:30 | sensor_1  | 42.5  | 42.5           |
    | 1234567891 | 2009-02-13 23:31:31 | sensor_2  | 38.2  | 38.2           |
    """
    import duckdb

    con = duckdb.connect()
    con.register("bronze_raw", bronze_data)

    # Transform with deduplication (keep dateTime for partitioning)
    result = con.execute(
        """
        WITH parsed AS (
            -- Step 1: Parse and filter raw data
            SELECT
                time AS time,
                dateTime AS dateTime,
                sensors AS signal,
                TRY_CAST(value AS DOUBLE) AS value,
                TRY_CAST(value AS DOUBLE) AS value_original
            FROM bronze_raw
        ),
        filtered AS (
            -- Step 2: Remove nulls and invalid values
            SELECT time, dateTime, signal, value, value_original
            FROM parsed
            WHERE value IS NOT NULL
              AND time IS NOT NULL
              AND dateTime IS NOT NULL
              AND signal IS NOT NULL
        ),
        ranked AS (
            -- Step 3: Deduplicate by signal+time, keeping highest value
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY signal, time
                    ORDER BY value DESC
                ) AS rn
            FROM filtered
        )
        -- Step 4: Final selection with deduplication
        SELECT
            time,
            dateTime,
            signal,
            value,
            value_original
        FROM ranked
        WHERE rn = 1
            and dateTime >= CURRENT_DATE
        """,
    ).arrow()

    return result
