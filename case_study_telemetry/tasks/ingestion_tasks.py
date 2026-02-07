"""Data ingestion tasks for the WAP pattern."""

import os
from typing import Any

import bauplan
from prefect import task
from prefect.logging import get_run_logger

from case_study_telemetry.config import get_config
from case_study_telemetry.models import BronzeClientTelemetry


@task(name="simulate-new-data", retries=0, retry_delay_seconds=30)
def simulate_new_data(
    s3_uri: str,
) -> dict[str, Any]:
    """Simulate new data arrival in the S3 bucket.

    This is a placeholder function that simulates the arrival of new data
    in the specified S3 URI. In a real-world scenario, this could involve
    copying files, generating data, or triggering an external process.

    Args:
        s3_uri: The S3 URI where new data is to be simulated.
    Returns:
        Dictionary with simulation statistics.
    """
    logger = get_run_logger()
    logger.info(f"Simulating new data arrival at {s3_uri}")
    config = get_config()

    # Placeholder logic for simulation
    # In a real implementation, this could copy files or generate data
    simulated_rows = 1000  # Example: number of rows "simulated"

    BronzeClientTelemetry.generate_sample_data(n_rows=simulated_rows).write_parquet(
        f"{s3_uri.rstrip('/')}/bronze_telemetry.parquet", storage_options=config.s3_storage_options
    )

    stats: dict[str, Any] = {
        "s3_uri": s3_uri,
        "rows_simulated": simulated_rows,
    }

    logger.info(f"Simulation complete: {stats}")
    return stats


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

    api_key = os.getenv("BAUPLAN_API_KEY")
    if not api_key:
        raise ValueError("BAUPLAN_API_KEY environment variable is not set")
    client = bauplan.Client(api_key=api_key)

    logger.info(f"Creating table {full_table_name}...")

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
