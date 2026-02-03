"""Prefect tasks for the WAP telemetry pipeline."""

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
from case_study_telemetry.tasks.ingestion_tasks import ensure_table_exists, ingest_from_s3
from case_study_telemetry.tasks.publish_tasks import diff_branch, merge_to_main
from case_study_telemetry.tasks.transformation_tasks import run_transformations

__all__ = [
    "AuditResult",
    "aggregate_audit_results",
    "check_no_duplicates",
    "check_no_null_signal",
    "check_no_null_time",
    "check_no_null_value",
    "check_row_count",
    "create_staging_branch",
    "delete_branch",
    "diff_branch",
    "ensure_table_exists",
    "ingest_from_s3",
    "merge_to_main",
    "run_transformations",
]
