"""Data ingestion tasks for the WAP pattern."""

from typing import Any

import bauplan
from prefect import task
from prefect.logging import get_run_logger


@task(name="ingest-from-s3", retries=0, retry_delay_seconds=30)
def ingest_from_s3(
    s3_uri: str,
    namespace: str,
    table_name: str,
    branch: str,
    file_pattern: str = "*.parquet",
) -> dict[str, Any]:
    """Ingest data from S3 into a Bauplan table on the staging branch.

    Creates the table if it doesn't exist, or replaces it if it does.
    The table schema is inferred from the parquet files.

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

    # Create table from S3 (this both creates the table and imports the data)
    # Using replace=True to handle the case where the table already exists
    table = client.create_table(
        table=full_table_name,
        search_uri=source_path,
        branch=branch,
        replace=True,
    )

    logger.info(f"Table {full_table_name} created successfully.")

    client.import_data(
        table=full_table_name,
        search_uri=source_path,
        branch=branch,
    )
    logger.info(f"Data imported into {full_table_name} successfully.")

    stats: dict[str, Any] = {
        "table": full_table_name,
        "branch": branch,
        "source": source_path,
        "table_created": table.name if table else full_table_name,
    }

    logger.info(f"Ingestion complete: {stats}")
    return stats
