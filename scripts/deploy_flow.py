#!/usr/bin/env python
"""Deploy the WAP telemetry flow to Prefect."""

from case_study_telemetry.flows.wap_telemetry_flow import wap_telemetry_pipeline


def main() -> None:
    """Deploy the WAP telemetry pipeline to Prefect."""
    # Serve the flow directly - this handles deployment internally
    wap_telemetry_pipeline.serve(
        name="wap-telemetry-deployment",
        tags=["wap", "telemetry", "etl"],
        parameters={
            "on_success": "inspect",  # Default to inspect mode for safety
            "on_failure": "keep",  # Keep branches for debugging by default
        },
    )


if __name__ == "__main__":
    main()
