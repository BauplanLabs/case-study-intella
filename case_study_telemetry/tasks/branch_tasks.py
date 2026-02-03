"""Bauplan branch management tasks for the WAP pattern."""

import uuid
from datetime import UTC, datetime

import bauplan
from prefect import task
from prefect.logging import get_run_logger


@task(name="create-staging-branch", retries=2, retry_delay_seconds=5)
def create_staging_branch(prefix: str = "wap-telemetry") -> str:
    """Create an isolated staging branch for WAP operations.

    Args:
        prefix: Prefix for the branch name.

    Returns:
        The name of the created branch.
    """
    logger = get_run_logger()

    # Generate unique branch name with timestamp and UUID
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    branch_name = f"{prefix}-{timestamp}-{unique_id}"

    logger.info(f"Creating staging branch: {branch_name}")

    client = bauplan.Client()
    client.create_branch(branch=branch_name, from_ref="main")

    logger.info(f"Successfully created branch: {branch_name}")
    return branch_name


@task(name="delete-branch", retries=2, retry_delay_seconds=5)
def delete_branch(branch_name: str) -> bool:
    """Delete a staging branch.

    Args:
        branch_name: Name of the branch to delete.

    Returns:
        True if deletion was successful.
    """
    logger = get_run_logger()
    logger.info(f"Deleting branch: {branch_name}")

    client = bauplan.Client()
    client.delete_branch(branch=branch_name)

    logger.info(f"Successfully deleted branch: {branch_name}")
    return True
