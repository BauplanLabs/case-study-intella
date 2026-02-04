"""Data transformation tasks for the WAP pattern."""

from pathlib import Path
from typing import Any

import bauplan
from prefect import task
from prefect.logging import get_run_logger


@task(name="run-transformations", retries=0, retry_delay_seconds=30)
def run_transformations(
    namespace: str,
    source_table: str,
    target_table: str,
    branch: str,
) -> dict[str, Any]:
    """Run Bauplan pipeline for Bronze to Silver transformation.

    Executes the telemetry_bronze_to_silver pipeline which:
    1. Maps columns (sensors -> signal)
    2. Parses values from string to float
    3. Removes null values
    4. Deduplicates by (signal, time), keeping highest value

    Bronze schema: time, dateTime, sensors, id, value, readId
    Silver schema: time, signal, value, value_original

    Args:
        namespace: The Bauplan namespace.
        source_table: The source table name (Bronze schema).
        target_table: The target table name (Silver schema).
        branch: The staging branch.

    Returns:
        Dictionary with transformation statistics.
    """
    logger = get_run_logger()
    source_full = f"{namespace}.{source_table}"
    target_full = f"{namespace}.{target_table}"

    logger.info(f"Running transformations on {source_full} -> {target_full}")

    # Get the pipeline project directory
    repo_root = Path(__file__).parent.parent.parent
    pipeline_dir = repo_root / "pipelines" / "telemetry_bronze_to_silver"

    if not pipeline_dir.exists():
        raise FileNotFoundError(f"Pipeline directory not found: {pipeline_dir}")

    logger.info(f"Pipeline directory: {pipeline_dir}")

    # Run the Bauplan pipeline
    client = bauplan.Client()

    try:
        logger.info(f"Executing pipeline on branch {branch}")
        run_state = client.run(
            project_dir=str(pipeline_dir),
            ref=branch,
            namespace=namespace,
        )

        # Check if the run succeeded
        job_status = str(run_state.job_status).lower()
        logger.info(f"Pipeline execution status: {run_state.job_status}")

        if job_status != "success":
            raise RuntimeError(f"Pipeline execution failed with status: {run_state.job_status}")

        # Get row count from the created table
        count_sql = f"SELECT COUNT(*) AS row_count FROM {target_full}"
        count_result = client.query(query=count_sql, ref=branch)
        row_count = int(count_result.column("row_count")[0].as_py()) if count_result else 0

        stats: dict[str, Any] = {
            "source_table": source_full,
            "target_table": target_full,
            "branch": branch,
            "rows_transformed": row_count,
            "job_id": run_state.job_id,
        }

        logger.info(f"Transformation complete: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Failed to run transformation pipeline: {e}")
        raise
