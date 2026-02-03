"""Data ingestion tasks for the WAP pattern."""

from typing import Any

import bauplan
from prefect import task
from prefect.logging import get_run_logger


@task(name="ensure-table-exists", retries=2, retry_delay_seconds=5)
def ensure_table_exists(
    namespace: str,
    table_name: str,
    branch: str = "main",
) -> bool:
    """Ensure the target table exists in the specified namespace.

    This simulates a production environment where the table schema is predefined.
    In a real scenario, this would be handled by infrastructure-as-code.

    Args:
        namespace: The Bauplan namespace.
        table_name: The table name.
        branch: The branch to check on.

    Returns:
        True if the table exists or was created successfully.
    """
    logger = get_run_logger()
    full_table_name = f"{namespace}.{table_name}"
    logger.info(f"Checking if table exists: {full_table_name} on branch {branch}")

    client = bauplan.Client()

    # Check if table exists
    try:
        client.get_table(table=full_table_name, ref=branch)
        logger.info(f"Table {full_table_name} already exists")
        return True
    except Exception:
        logger.info(f"Table {full_table_name} does not exist, will be created during ingestion")
        return True


@task(name="ingest-from-s3", retries=2, retry_delay_seconds=30)
def ingest_from_s3(
    s3_uri: str,
    namespace: str,
    table_name: str,
    branch: str,
    file_pattern: str = "*.parquet",
) -> dict[str, Any]:
    """Ingest data from S3 into a Bauplan table on the staging branch.

    Args:
        s3_uri: The S3 URI to ingest from (e.g., s3://bucket/path/).
        namespace: The Bauplan namespace.
        table_name: The target table name.
        branch: The staging branch to ingest into.
        file_pattern: Glob pattern for files to ingest.

    Returns:
        Dictionary with ingestion statistics.
    """
    logger = get_run_logger()
    full_table_name = f"{namespace}.{table_name}"
    source_path = f"{s3_uri.rstrip('/')}/{file_pattern}"

    logger.info(f"Ingesting from {source_path} into {full_table_name} on branch {branch}")

    client = bauplan.Client()

    # Import data from S3 to the staging branch
    result = client.import_data(
        table=full_table_name,
        search_uri=source_path,
        branch=branch,
    )

    stats: dict[str, Any] = {
        "table": full_table_name,
        "branch": branch,
        "source": source_path,
        "rows_ingested": getattr(result, "rows_ingested", 0),
    }

    logger.info(f"Ingestion complete: {stats}")
    return stats
