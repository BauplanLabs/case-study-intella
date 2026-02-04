"""Main WAP (Write-Audit-Publish) flow for telemetry data processing."""

from dataclasses import dataclass, field
from typing import Any, Literal

from dotenv import load_dotenv
from prefect import flow
from prefect.logging import get_run_logger

from case_study_telemetry.config import get_config
from case_study_telemetry.tasks.audit_tasks import (
    AuditResult,
    aggregate_audit_results,
    check_no_duplicates,
    check_no_null_signal,
    check_no_null_time,
    check_no_null_value,
    check_row_count,
)
from case_study_telemetry.tasks.branch_tasks import create_staging_branch, delete_branch
from case_study_telemetry.tasks.ingestion_tasks import ingest_from_s3
from case_study_telemetry.tasks.publish_tasks import merge_to_main
from case_study_telemetry.tasks.transformation_tasks import run_transformations


@dataclass
class WAPResult:
    """Result of the WAP pipeline execution."""

    success: bool
    branch: str
    phase: str  # "write", "audit", "publish"
    ingestion_stats: dict[str, Any] | None = None
    transformation_stats: dict[str, Any] | None = None
    audit_summary: dict[str, Any] | None = None
    merge_result: dict[str, Any] | None = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)


@flow(name="wap-telemetry-pipeline", log_prints=True)
def wap_telemetry_pipeline(
    s3_source_bucket: str | None = None,
    s3_source_path: str | None = None,
    namespace: str | None = None,
    target_table: str | None = None,
    on_success: Literal["inspect", "merge"] | None = None,
    on_failure: Literal["keep", "delete"] | None = None,
) -> WAPResult:
    """Execute the Write-Audit-Publish pipeline for telemetry data.

    This flow implements the WAP pattern:
    1. WRITE: Create branch -> Ingest from S3 -> Transform (Bronze -> Silver)
    2. AUDIT: Run all quality checks in parallel
    3. PUBLISH: Merge to main if all checks pass (based on on_success setting)

    Args:
        s3_source_bucket: S3 bucket containing source data (overrides config).
        s3_source_path: Path within the bucket (overrides config).
        namespace: Bauplan namespace (overrides config).
        target_table: Target table name (overrides config).
        on_success: Action on successful audit - "inspect" (show diff) or "merge" (publish).
        on_failure: Action on audit failure - "keep" (preserve branch) or "delete" (cleanup).

    Returns:
        WAPResult with execution details and status.
    """
    logger = get_run_logger()
    config = get_config()

    # Use provided values or fall back to config
    bucket = s3_source_bucket or config.s3_source_bucket
    path = s3_source_path or config.s3_source_path
    ns = namespace or config.bauplan_namespace
    table = target_table or config.bauplan_target_table
    success_action = on_success or config.wap_on_success
    failure_action = on_failure or config.wap_on_failure

    s3_uri = f"s3://{bucket}/{path.strip('/')}"
    bronze_table = f"{table}_bronze"  # Raw ingested data
    silver_table = table  # Transformed data

    logger.info("=" * 60)
    logger.info("WAP TELEMETRY PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Source: {s3_uri}")
    logger.info(f"Bronze: {ns}.{bronze_table}")
    logger.info(f"Silver: {ns}.{silver_table}")
    logger.info(f"On Success: {success_action}")
    logger.info(f"On Failure: {failure_action}")
    logger.info("=" * 60)

    branch: str = ""
    result = WAPResult(success=False, branch="", phase="write")

    try:
        # ==================== PHASE 1: WRITE ====================
        logger.info("")
        logger.info("PHASE 1: WRITE")
        logger.info("-" * 40)

        # Step 1.1: Create staging branch (username.wap-staging)
        branch = create_staging_branch()
        result.branch = branch
        logger.info(f"Created staging branch: {branch}")

        # Step 1.2: Ingest raw data from S3 (Bronze schema)
        # create_table handles both table creation and data import
        ingestion_stats = ingest_from_s3(
            s3_uri=s3_uri,
            namespace=ns,
            table_name=bronze_table,
            branch=branch,
            file_pattern=config.s3_source_pattern,
        )
        result.ingestion_stats = ingestion_stats
        logger.info(f"Ingested {ingestion_stats.get('rows_ingested', 'unknown')} rows")

        # Step 1.4: Run transformations (Bronze -> Silver)
        transformation_stats = run_transformations(
            namespace=ns,
            source_table=bronze_table,
            target_table=silver_table,
            branch=branch,
        )
        result.transformation_stats = transformation_stats
        logger.info(f"Transformed {transformation_stats.get('rows_transformed', 'unknown')} rows")

        # ==================== PHASE 2: AUDIT ====================
        result.phase = "audit"
        logger.info("")
        logger.info("PHASE 2: AUDIT")
        logger.info("-" * 40)

        # Run all audit checks on the Silver table
        audit_futures: list[AuditResult] = []

        # Submit all checks - they run in parallel
        null_time_result = check_no_null_time(namespace=ns, table_name=silver_table, branch=branch)
        null_value_result = check_no_null_value(
            namespace=ns, table_name=silver_table, branch=branch
        )
        null_signal_result = check_no_null_signal(
            namespace=ns, table_name=silver_table, branch=branch
        )
        duplicates_result = check_no_duplicates(
            namespace=ns, table_name=silver_table, branch=branch
        )
        row_count_result = check_row_count(namespace=ns, table_name=silver_table, branch=branch)

        audit_futures = [
            null_time_result,
            null_value_result,
            null_signal_result,
            duplicates_result,
            row_count_result,
        ]

        # Aggregate audit results
        audit_summary = aggregate_audit_results(audit_futures)
        result.audit_summary = audit_summary

        if not audit_summary["all_passed"]:
            result.success = False
            result.error = f"Audit failed: {audit_summary['failed_count']} checks failed"
            logger.error(result.error)

            # Handle failure action
            if failure_action == "delete":
                logger.info(f"Deleting branch {branch} (on_failure=delete)")
                delete_branch(branch)
                result.warnings.append(f"Branch {branch} deleted due to audit failure")
            else:
                logger.info(f"Keeping branch {branch} for debugging (on_failure=keep)")
                result.warnings.append(f"Branch {branch} preserved for debugging")

            return result

        logger.info("All audit checks PASSED")

        # ==================== PHASE 3: PUBLISH ====================
        result.phase = "publish"
        logger.info("")
        logger.info("PHASE 3: PUBLISH")
        logger.info("-" * 40)

        if success_action == "merge":
            # Merge to main after successful audits
            logger.info("Merging to main (on_success=merge)")
            merge_result = merge_to_main(branch)
            result.merge_result = merge_result
            result.success = True
            logger.info("Successfully merged to main!")

            # Clean up branch after merge
            logger.info(f"Cleaning up branch {branch}")
            delete_branch(branch)
        else:
            # Inspect mode - keep branch for manual review
            logger.info("Inspect mode (on_success=inspect)")
            logger.info(f"Branch {branch} ready for manual review")
            logger.info("Run the following commands to review and merge:")
            logger.info(f"  bauplan branch diff {branch} main")
            logger.info(f"  bauplan merge {branch} main")
            result.success = True
            result.warnings.append(f"Branch {branch} not merged (on_success=inspect)")

        logger.info("")
        logger.info("=" * 60)
        logger.info("WAP PIPELINE COMPLETE")
        logger.info("=" * 60)

        return result

    except Exception as e:
        logger.error(f"Pipeline failed during {result.phase} phase: {e}")
        result.success = False
        result.error = str(e)

        # Handle cleanup on exception
        if branch and failure_action == "delete":
            try:
                logger.info(f"Attempting to clean up branch {branch}")
                delete_branch(branch)
                result.warnings.append(f"Branch {branch} deleted after error")
            except Exception as cleanup_error:
                result.warnings.append(f"Failed to delete branch: {cleanup_error}")

        return result


if __name__ == "__main__":
    # Allow running directly for testing
    load_dotenv()
    result = wap_telemetry_pipeline()
    print(f"Pipeline result: {result}")
