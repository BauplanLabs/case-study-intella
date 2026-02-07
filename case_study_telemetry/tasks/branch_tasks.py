"""Bauplan branch management tasks for the WAP pattern."""

import os

import bauplan
from prefect import task
from prefect.logging import get_run_logger


@task(name="create-staging-branch", retries=0, retry_delay_seconds=5)
def create_staging_branch(branch_suffix: str = "wap-staging") -> str:
    """Create or reset an isolated staging branch for WAP operations.

    Uses a fixed branch name based on username to allow reuse across runs.
    If the branch already exists, it will be deleted and recreated from main.

    Args:
        branch_suffix: Suffix for the branch name (prefixed with username).

    Returns:
        The name of the created branch.
    """
    logger = get_run_logger()

    # Initialize Bauplan client with API key from environment
    api_key = os.getenv("BAUPLAN_API_KEY")
    if not api_key:
        raise ValueError("BAUPLAN_API_KEY environment variable is not set")
    client = bauplan.Client(api_key=api_key)

    # Get username from Bauplan
    user = client.info().user
    if not user:
        raise ValueError("Could not retrieve user from Bauplan client.")

    username = user.username

    if not username:
        raise ValueError("Bauplan user does not have a valid username.")

    # Fixed branch name: username.suffix
    branch_name = f"{username}.{branch_suffix}"

    logger.info(f"Setting up staging branch: {branch_name}")

    # Check if branch already exists and delete it
    if client.has_branch(branch=branch_name):
        logger.info(f"Branch {branch_name} already exists, deleting it first")
        client.delete_branch(branch=branch_name)

    # Create fresh branch from main
    client.create_branch(branch=branch_name, from_ref="main")

    logger.info(f"Successfully created branch: {branch_name}")
    return branch_name


@task(name="delete-branch", retries=0, retry_delay_seconds=5)
def delete_branch(branch_name: str) -> bool:
    """Delete a staging branch.

    Args:
        branch_name: Name of the branch to delete.

    Returns:
        True if deletion was successful.
    """
    logger = get_run_logger()

    logger.info(f"Deleting branch: {branch_name}")

    # Initialize Bauplan client with API key from environment
    api_key = os.getenv("BAUPLAN_API_KEY")
    if not api_key:
        raise ValueError("BAUPLAN_API_KEY environment variable is not set")
    client = bauplan.Client(api_key=api_key)

    # Only delete if it exists
    if client.has_branch(branch=branch_name):
        client.delete_branch(branch=branch_name)
        logger.info(f"Successfully deleted branch: {branch_name}")
    else:
        logger.info(f"Branch {branch_name} does not exist, skipping delete")

    return True
