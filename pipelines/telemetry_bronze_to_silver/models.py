"""Bauplan models for Bronze to Silver telemetry transformation.

This pipeline transforms raw telemetry data (Bronze schema) into a clean,
deduplicated format (Silver schema).

DAG:
    [telemetry.signal_bronze] -> [signal] (Silver)

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
    columns=["time", "signal", "value", "value_original"],
    materialization_strategy="REPLACE",
)
@bauplan.python("3.12", pip={"duckdb": "1.1.3"})
def signal(
    bronze_data=bauplan.Model(
        "signal_bronze",
        columns=["time", "dateTime", "sensors", "value"],
    ),
):
    """Transform Bronze telemetry data to Silver schema with deduplication.

    Reads from signal_bronze and applies:
    - Column rename: sensors -> signal
    - Type casting: value (string) -> value (float)
    - Null removal
    - Deduplication by (signal, time), keeping highest value

    Output Schema:
    | time       | signal    | value | value_original |
    | ---------- | --------- | ----- | -------------- |
    | 1234567890 | sensor_1  | 42.5  | 42.5           |
    | 1234567891 | sensor_2  | 38.2  | 38.2           |
    """
    import duckdb

    # Register bronze data as a DuckDB relation
    con = duckdb.connect()
    con.register("bronze_raw", bronze_data)

    # SQL transformation with deduplication
    result = con.execute(
        """
        WITH parsed AS (
            -- Step 1: Parse and filter raw data
            SELECT
                time AS time,
                sensors AS signal,
                TRY_CAST(value AS DOUBLE) AS value,
                TRY_CAST(value AS DOUBLE) AS value_original,
                dateTime
            FROM bronze_raw
        ),
        filtered AS (
            -- Step 2: Remove nulls and invalid values
            SELECT time, signal, value, value_original
            FROM parsed
            WHERE value IS NOT NULL
              AND time IS NOT NULL
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
            signal,
            value,
            value_original
        FROM ranked
        WHERE rn = 1
        """,
    ).arrow()

    return result
