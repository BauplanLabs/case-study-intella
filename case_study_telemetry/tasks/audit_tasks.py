"""Data quality audit tasks for the WAP pattern."""

from dataclasses import dataclass
from typing import Any

import bauplan
import pyarrow as pa
from prefect import task
from prefect.logging import get_run_logger

from case_study_telemetry.models import SilverClientTelemetry


@dataclass
class AuditResult:
    """Result of a single audit check."""

    check_name: str
    passed: bool
    message: str
    details: dict[str, Any] | None = None


def _get_scalar_from_table(table: pa.Table, column: str, default: int = 0) -> int:
    """Extract a scalar value from a single-row PyArrow table.

    Args:
        table: PyArrow table with query results.
        column: Column name to extract.
        default: Default value if extraction fails.

    Returns:
        The scalar value as an integer.
    """
    if table is None or len(table) == 0:
        return default
    return int(table.column(column)[0].as_py())


@task(name="check-no-null-time", retries=0)
def check_no_null_time(
    namespace: str,
    table_name: str,
    branch: str,
) -> AuditResult:
    """Check that no rows have null time values.

    Args:
        namespace: The Bauplan namespace.
        table_name: The table to check.
        branch: The branch to check on.

    Returns:
        AuditResult with check status.
    """
    logger = get_run_logger()
    full_table = f"{namespace}.{table_name}"
    check_name = "no_null_time"
    time_col = SilverClientTelemetry.time_col

    logger.info(f"Running {check_name} check on {full_table}")

    sql = f"""
    SELECT COUNT(*) AS null_count
    FROM {full_table}
    WHERE {time_col} IS NULL
    """

    client = bauplan.Client()
    result = client.query(query=sql, ref=branch)

    null_count = _get_scalar_from_table(result, "null_count")
    passed = null_count == 0

    msg = (
        f"Found {null_count} rows with null {time_col}"
        if not passed
        else f"All {time_col} values are non-null"
    )
    audit_result = AuditResult(
        check_name=check_name,
        passed=passed,
        message=msg,
        details={"null_count": null_count, "table": full_table, "column": time_col},
    )

    logger.info(f"{check_name}: {'PASSED' if passed else 'FAILED'} - {audit_result.message}")
    return audit_result


@task(name="check-no-null-value", retries=0)
def check_no_null_value(
    namespace: str,
    table_name: str,
    branch: str,
) -> AuditResult:
    """Check that no rows have null value values.

    Args:
        namespace: The Bauplan namespace.
        table_name: The table to check.
        branch: The branch to check on.

    Returns:
        AuditResult with check status.
    """
    logger = get_run_logger()
    full_table = f"{namespace}.{table_name}"
    check_name = "no_null_value"
    value_col = SilverClientTelemetry.value_col

    logger.info(f"Running {check_name} check on {full_table}")

    sql = f"""
    SELECT COUNT(*) AS null_count
    FROM {full_table}
    WHERE {value_col} IS NULL
    """

    client = bauplan.Client()
    result = client.query(query=sql, ref=branch)

    null_count = _get_scalar_from_table(result, "null_count")
    passed = null_count == 0

    msg = (
        f"Found {null_count} rows with null {value_col}"
        if not passed
        else f"All {value_col} fields are non-null"
    )
    audit_result = AuditResult(
        check_name=check_name,
        passed=passed,
        message=msg,
        details={"null_count": null_count, "table": full_table, "column": value_col},
    )

    logger.info(f"{check_name}: {'PASSED' if passed else 'FAILED'} - {audit_result.message}")
    return audit_result


@task(name="check-no-null-signal", retries=0)
def check_no_null_signal(
    namespace: str,
    table_name: str,
    branch: str,
) -> AuditResult:
    """Check that no rows have null signal values.

    Args:
        namespace: The Bauplan namespace.
        table_name: The table to check.
        branch: The branch to check on.

    Returns:
        AuditResult with check status.
    """
    logger = get_run_logger()
    full_table = f"{namespace}.{table_name}"
    check_name = "no_null_signal"
    signal_col = SilverClientTelemetry.signal_col

    logger.info(f"Running {check_name} check on {full_table}")

    sql = f"""
    SELECT COUNT(*) AS null_count
    FROM {full_table}
    WHERE {signal_col} IS NULL
    """

    client = bauplan.Client()
    result = client.query(query=sql, ref=branch)

    null_count = _get_scalar_from_table(result, "null_count")
    passed = null_count == 0

    msg = (
        f"Found {null_count} rows with null {signal_col}"
        if not passed
        else f"All {signal_col} fields are non-null"
    )
    audit_result = AuditResult(
        check_name=check_name,
        passed=passed,
        message=msg,
        details={"null_count": null_count, "table": full_table, "column": signal_col},
    )

    logger.info(f"{check_name}: {'PASSED' if passed else 'FAILED'} - {audit_result.message}")
    return audit_result


@task(name="check-no-duplicates", retries=0)
def check_no_duplicates(
    namespace: str,
    table_name: str,
    branch: str,
) -> AuditResult:
    """Check that no duplicate (time, signal) entries exist.

    Args:
        namespace: The Bauplan namespace.
        table_name: The table to check.
        branch: The branch to check on.

    Returns:
        AuditResult with check status.
    """
    logger = get_run_logger()
    full_table = f"{namespace}.{table_name}"
    check_name = "no_duplicates"
    key_cols = SilverClientTelemetry.key_columns()

    logger.info(f"Running {check_name} check on {full_table}")

    key_cols_str = ", ".join(key_cols)
    sql = f"""
    SELECT COUNT(*) AS duplicate_count
    FROM (
        SELECT {key_cols_str}, COUNT(*) AS cnt
        FROM {full_table}
        GROUP BY {key_cols_str}
        HAVING COUNT(*) > 1
    ) duplicates
    """

    client = bauplan.Client()
    result = client.query(query=sql, ref=branch)

    duplicate_count = _get_scalar_from_table(result, "duplicate_count")
    passed = duplicate_count == 0

    msg = (
        f"Found {duplicate_count} duplicate ({key_cols_str}) combinations"
        if not passed
        else "No duplicate entries found"
    )
    audit_result = AuditResult(
        check_name=check_name,
        passed=passed,
        message=msg,
        details={"duplicate_count": duplicate_count, "table": full_table, "keys": key_cols},
    )

    logger.info(f"{check_name}: {'PASSED' if passed else 'FAILED'} - {audit_result.message}")
    return audit_result


@task(name="check-row-count", retries=0)
def check_row_count(
    namespace: str,
    table_name: str,
    branch: str,
    min_rows: int = 1,
) -> AuditResult:
    """Check that the table has at least min_rows rows.

    Args:
        namespace: The Bauplan namespace.
        table_name: The table to check.
        branch: The branch to check on.
        min_rows: Minimum number of rows required.

    Returns:
        AuditResult with check status.
    """
    logger = get_run_logger()
    full_table = f"{namespace}.{table_name}"
    check_name = "row_count"

    logger.info(f"Running {check_name} check on {full_table}")

    sql = f"""
    SELECT COUNT(*) AS row_count
    FROM {full_table}
    """

    client = bauplan.Client()
    result = client.query(query=sql, ref=branch)

    row_count = _get_scalar_from_table(result, "row_count")
    passed = row_count >= min_rows

    msg = (
        f"Table has {row_count} rows (minimum: {min_rows})"
        if not passed
        else f"Table has {row_count} rows"
    )
    audit_result = AuditResult(
        check_name=check_name,
        passed=passed,
        message=msg,
        details={"row_count": row_count, "min_rows": min_rows, "table": full_table},
    )

    logger.info(f"{check_name}: {'PASSED' if passed else 'FAILED'} - {audit_result.message}")
    return audit_result


@task(name="aggregate-audit-results")
def aggregate_audit_results(results: list[AuditResult]) -> dict[str, Any]:
    """Aggregate all audit results into a summary.

    Args:
        results: List of individual audit results.

    Returns:
        Dictionary with aggregated audit summary.
    """
    logger = get_run_logger()

    all_passed = all(r.passed for r in results)
    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count

    summary: dict[str, Any] = {
        "all_passed": all_passed,
        "total_checks": len(results),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": [
            {
                "name": r.check_name,
                "passed": r.passed,
                "message": r.message,
            }
            for r in results
        ],
    }

    if all_passed:
        logger.info(f"All {len(results)} audit checks PASSED")
    else:
        failed_checks = [r.check_name for r in results if not r.passed]
        logger.warning(
            f"Audit FAILED: {failed_count}/{len(results)} checks failed: {failed_checks}"
        )

    return summary
