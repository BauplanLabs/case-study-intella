"""Configuration management for the WAP telemetry pipeline."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class WAPConfig(BaseSettings):
    """Configuration for the WAP telemetry pipeline.

    All settings are loaded from environment variables with the specified prefixes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Bauplan Configuration
    bauplan_api_key: str = ""
    bauplan_namespace: str = "telemetry"
    bauplan_target_table: str = "signals"

    # S3 Source Configuration
    s3_source_bucket: str = ""
    s3_source_path: str = "telemetry/raw/"
    s3_source_pattern: str = "*.parquet"

    # Prefect Configuration
    prefect_api_url: str = "http://localhost:4200/api"

    # WAP Behavior
    wap_on_success: Literal["inspect", "merge"] = "inspect"
    wap_on_failure: Literal["keep", "delete"] = "keep"

    # Transformation Parameters
    transform_min_date: str = "1980-01-01"

    @property
    def s3_source_uri(self) -> str:
        """Construct the full S3 URI for the source data."""
        return f"s3://{self.s3_source_bucket}/{self.s3_source_path}"

    @property
    def full_table_name(self) -> str:
        """Construct the fully qualified table name."""
        return f"{self.bauplan_namespace}.{self.bauplan_target_table}"


@lru_cache
def get_config() -> WAPConfig:
    """Get the cached configuration instance."""
    return WAPConfig()
