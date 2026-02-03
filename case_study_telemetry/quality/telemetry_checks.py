"""SQL-based quality check definitions for telemetry data.

These SQL templates can be used directly or through the audit tasks.
Uses the Silver schema (time, signal, value, value_original).
"""

from dataclasses import dataclass, field

from case_study_telemetry.models import SilverClientTelemetry

# SQL Templates for quality checks using Silver schema column names
NO_NULL_TIME_SQL = f"""
SELECT COUNT(*) AS violation_count
FROM {{table}}
WHERE {SilverClientTelemetry.time_col} IS NULL
"""

NO_NULL_VALUE_SQL = f"""
SELECT COUNT(*) AS violation_count
FROM {{table}}
WHERE {SilverClientTelemetry.value_col} IS NULL
"""

NO_NULL_SIGNAL_SQL = f"""
SELECT COUNT(*) AS violation_count
FROM {{table}}
WHERE {SilverClientTelemetry.signal_col} IS NULL
"""

NO_DUPLICATES_SQL = f"""
SELECT COUNT(*) AS violation_count
FROM (
    SELECT {", ".join(SilverClientTelemetry.key_columns())}, COUNT(*) AS cnt
    FROM {{table}}
    GROUP BY {", ".join(SilverClientTelemetry.key_columns())}
    HAVING COUNT(*) > 1
) duplicates
"""

ROW_COUNT_SQL = """
SELECT COUNT(*) AS row_count
FROM {table}
"""


@dataclass
class QualityCheck:
    """Definition of a single quality check."""

    name: str
    description: str
    sql_template: str
    violation_column: str = "violation_count"
    threshold: int = 0
    comparison: str = "eq"  # eq, gt, lt, gte, lte


@dataclass
class TelemetryQualityChecks:
    """Collection of quality checks for the telemetry Silver table."""

    table: str
    checks: list[QualityCheck] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize default quality checks for telemetry data."""
        if not self.checks:
            self.checks = [
                QualityCheck(
                    name="no_null_time",
                    description=f"All rows must have a non-null {SilverClientTelemetry.time_col}",
                    sql_template=NO_NULL_TIME_SQL,
                ),
                QualityCheck(
                    name="no_null_value",
                    description=f"All rows must have a non-null {SilverClientTelemetry.value_col}",
                    sql_template=NO_NULL_VALUE_SQL,
                ),
                QualityCheck(
                    name="no_null_signal",
                    description=f"All rows must have a non-null {SilverClientTelemetry.signal_col}",
                    sql_template=NO_NULL_SIGNAL_SQL,
                ),
                QualityCheck(
                    name="no_duplicates",
                    description=(
                        f"No duplicate ({', '.join(SilverClientTelemetry.key_columns())}) "
                        "combinations"
                    ),
                    sql_template=NO_DUPLICATES_SQL,
                ),
                QualityCheck(
                    name="has_rows",
                    description="Table must have at least one row",
                    sql_template=ROW_COUNT_SQL,
                    violation_column="row_count",
                    threshold=1,
                    comparison="gte",
                ),
            ]

    def get_sql(self, check_name: str) -> str:
        """Get the SQL for a specific check with table substituted.

        Args:
            check_name: Name of the check.

        Returns:
            SQL query string with table name substituted.

        Raises:
            KeyError: If check_name is not found.
        """
        for check in self.checks:
            if check.name == check_name:
                return check.sql_template.format(table=self.table)
        raise KeyError(f"Check '{check_name}' not found")

    def all_check_names(self) -> list[str]:
        """Get all check names.

        Returns:
            List of check names.
        """
        return [check.name for check in self.checks]
