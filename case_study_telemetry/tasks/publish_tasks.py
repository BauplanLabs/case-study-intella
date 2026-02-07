"""Publish tasks for the WAP pattern - merging to main."""

import os
from typing import Any

import bauplan
from prefect import task
from prefect.logging import get_run_logger


@task(name="merge-to-main", retries=0, retry_delay_seconds=10)
def merge_to_main(branch: str) -> dict[str, Any]:
    """Merge the staging branch into main (publish).

    This is the final step of the WAP pattern - only called after all audits pass.

    Args:
        branch: The staging branch to merge.

    Returns:
        Dictionary with merge result information.
    """
    logger = get_run_logger()
    logger.info(f"Merging branch {branch} into main")

    api_key = os.getenv("BAUPLAN_API_KEY")
    if not api_key:
        raise ValueError("BAUPLAN_API_KEY environment variable is not set")
    client = bauplan.Client(api_key=api_key)

    # Perform the merge using the correct parameter names
    merge_result = client.merge_branch(source_ref=branch, into_branch="main")

    result_info: dict[str, Any] = {
        "branch": branch,
        "merged_into": "main",
        "success": True,
        "message": f"Successfully merged {branch} into main",
        "result": str(merge_result),
    }

    logger.info(f"Merge successful: {branch} -> main")
    return result_info
