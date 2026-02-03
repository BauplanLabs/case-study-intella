"""Data transformation tasks for the WAP pattern."""

from typing import Any

import bauplan
from prefect import task
from prefect.logging import get_run_logger

from case_study_telemetry.models import BronzeClientTelemetry, SilverClientTelemetry


@task(name="run-transformations", retries=0, retry_delay_seconds=30)
def run_transformations(
    namespace: str,
    source_table: str,
    target_table: str,
    branch: str,
    min_date: str = "1980-01-01",
) -> dict[str, Any]:
    """Run SQL-based transformations from Bronze to Silver schema.

    Transformations include:
    1. Time range filtering (after min_date)
    2. Column mapping (sensors -> signal)
    3. Value parsing from string to float
    4. Deduplication (unique by signal+time, keep highest value)

    Bronze schema: time, dateTime, sensors, id, value, readId
    Silver schema: time, signal, value, value_original

    Args:
        namespace: The Bauplan namespace.
        source_table: The source table name (Bronze schema).
        target_table: The target table name (Silver schema).
        branch: The staging branch.
        min_date: Minimum date for time filtering.

    Returns:
        Dictionary with transformation statistics.
    """
    logger = get_run_logger()
    source_full = f"{namespace}.{source_table}"
    target_full = f"{namespace}.{target_table}"

    # Column references from models
    bronze = BronzeClientTelemetry
    silver = SilverClientTelemetry

    logger.info(f"Running transformations on {source_full} -> {target_full}")
    logger.info(f"Bronze columns: {list(bronze.polars_schema().names())}")
    logger.info(f"Silver columns: {list(silver.polars_schema().names())}")

    # SQL transformation query: Bronze -> Silver
    transform_sql = f"""
    WITH parsed AS (
        -- Step 1: Parse and filter raw data
        SELECT
            {bronze.time_col} AS {silver.time_col},
            {bronze.sensors_col} AS {silver.signal_col},
            TRY_CAST({bronze.value_col} AS DOUBLE) AS {silver.value_col},
            TRY_CAST({bronze.value_col} AS DOUBLE) AS {silver.value_original_col}
        FROM {source_full}
        WHERE {bronze.date_time_col} >= TIMESTAMP '{min_date}'
    ),
    filtered AS (
        -- Step 2: Remove nulls and invalid values
        SELECT *
        FROM parsed
        WHERE {silver.value_col} IS NOT NULL
          AND {silver.time_col} IS NOT NULL
          AND {silver.signal_col} IS NOT NULL
    ),
    ranked AS (
        -- Step 3: Deduplicate by signal+time, keeping highest value
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY {silver.signal_col}, {silver.time_col}
                ORDER BY {silver.value_col} DESC
            ) AS rn
        FROM filtered
    )
    -- Step 4: Final selection with deduplication
    SELECT
        {silver.time_col},
        {silver.signal_col},
        {silver.value_col},
        {silver.value_original_col}
    FROM ranked
    WHERE rn = 1
    """

    client = bauplan.Client()

    # Execute the transformation as a query
    logger.info("Executing transformation SQL...")
    result = client.query(query=transform_sql, ref=branch)

    # Get row count from the result
    row_count = len(result) if result is not None else 0

    stats: dict[str, Any] = {
        "source_table": source_full,
        "target_table": target_full,
        "branch": branch,
        "rows_transformed": row_count,
        "min_date": min_date,
    }

    logger.info(f"Transformation complete: {stats}")
    return stats
