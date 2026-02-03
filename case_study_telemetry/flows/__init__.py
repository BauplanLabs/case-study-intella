"""Prefect flows for the WAP telemetry pipeline."""

from case_study_telemetry.flows.wap_telemetry_flow import WAPResult, wap_telemetry_pipeline

__all__ = [
    "WAPResult",
    "wap_telemetry_pipeline",
]
