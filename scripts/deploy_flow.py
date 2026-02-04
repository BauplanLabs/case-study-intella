#!/usr/bin/env python
"""Deploy the WAP telemetry flow to Prefect."""

from datetime import timedelta

from prefect.schedules import Schedule

from case_study_telemetry.flows.wap_telemetry_flow import wap_telemetry_pipeline


def main() -> None:
    """Deploy the WAP telemetry pipeline to Prefect."""
    # Serve the flow directly - this handles deployment internally
    wap_telemetry_pipeline.serve(
        name="wap-telemetry-deployment",
        tags=["wap", "telemetry", "etl"],
        parameters={
            "on_success": "merge",  # Default to merge mode for deployment
            "on_failure": "delete",  # Delete branches for cleanup by default
        },
        schedule=Schedule(interval=timedelta(minutes=5)),
    )


if __name__ == "__main__":
    main()
