"""Publish tasks for the WAP pattern - merging to main."""

import subprocess
from typing import Any

import bauplan
from prefect import task
from prefect.logging import get_run_logger


@task(name="diff-branch", retries=0)
def diff_branch(branch: str) -> dict[str, Any]:
    """Show the differences between the staging branch and main.

    This is the safety check before merging - always review before publishing.
    Uses the Bauplan CLI since there's no SDK method for branch diff.

    Args:
        branch: The staging branch to diff against main.

    Returns:
        Dictionary with diff information.
    """
    logger = get_run_logger()
    logger.info(f"Computing diff between {branch} and main")

    # Use CLI for diff since there's no SDK method
    try:
        result = subprocess.run(
            ["bauplan", "branch", "diff", branch, "main"],
            capture_output=True,
            text=True,
            check=True,
        )
        diff_output = result.stdout
    except subprocess.CalledProcessError as e:
        diff_output = f"Error running diff: {e.stderr}"
        logger.warning(diff_output)
    except FileNotFoundError:
        diff_output = "bauplan CLI not found - diff unavailable"
        logger.warning(diff_output)

    diff_info: dict[str, Any] = {
        "branch": branch,
        "base": "main",
        "summary": diff_output,
    }

    logger.info("Branch diff summary:")
    logger.info(f"Full diff:\n{diff_output}")

    return diff_info


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

    client = bauplan.Client()

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
