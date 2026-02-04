"""This module contains the BronzeClientTelemetry model definition."""

import random
from datetime import datetime, timedelta

import polars as pl


class BronzeClientTelemetry:
    """This class handles the BronzeClientTelemetry DataFrame."""

    time_col = "time"
    date_time_col = "dateTime"
    sensors_col = "sensors"
    id_col = "id"
    value_col = "value"
    read_id_col = "readId"

    @classmethod
    def polars_schema(cls) -> pl.Schema:
        """Returns the schema of the Dataframe."""
        return pl.Schema(
            {
                cls.time_col: pl.Int64,
                cls.date_time_col: pl.Datetime("ms"),
                cls.sensors_col: pl.String,
                cls.id_col: pl.String,
                cls.value_col: pl.String,
                cls.read_id_col: pl.Int64,
            }
        )

    @classmethod
    def generate_sample_data(cls, n_rows: int = 5) -> pl.DataFrame:
        """Generates a random DataFrame with the specified schema."""

        data = {
            cls.time_col: [random.randint(1000000000, 9999999999) for _ in range(n_rows)],
            cls.date_time_col: [
                datetime.now() + timedelta(minutes=random.randint(0, 1000)) for _ in range(n_rows)
            ],
            cls.sensors_col: [f"sensor_{random.randint(1, 10)}" for _ in range(n_rows)],
            cls.id_col: [f"id_{random.randint(1000, 9999)}" for _ in range(n_rows)],
            cls.value_col: [f"{random.uniform(0, 100):.2f}" for _ in range(n_rows)],
            cls.read_id_col: [random.randint(1, 1000) for _ in range(n_rows)],
        }

        return pl.DataFrame(data, schema=cls.polars_schema())


class SilverClientTelemetry:
    """This class handles the SilverClientTelemetry DataFrame."""

    date_time_col = "dateTime"
    signal_col = "signal"
    value_col = "value"
    value_original_col = "value_original"

    @classmethod
    def polars_schema(cls) -> pl.Schema:
        """Returns the schema of the Dataframe."""

        return pl.Schema(
            {
                cls.date_time_col: pl.Datetime("ms"),
                cls.signal_col: pl.String,
                cls.value_col: pl.Float32,
                cls.value_original_col: pl.Float32,
            }
        )

    @classmethod
    def key_columns(cls) -> list[str]:
        """Returns the keys of the DataFrame."""
        return [cls.date_time_col, cls.signal_col]

    @classmethod
    def generate_sample_data(cls, n_rows: int = 5) -> pl.DataFrame:
        """Generates a random DataFrame with the specified schema."""

        data = {
            cls.date_time_col: [
                datetime.now() + timedelta(minutes=random.randint(0, 1000)) for _ in range(n_rows)
            ],
            cls.signal_col: [f"signal_{random.randint(1, 10)}" for _ in range(n_rows)],
            cls.value_col: [random.uniform(0, 100) for _ in range(n_rows)],
            cls.value_original_col: [random.uniform(0, 100) for _ in range(n_rows)],
        }

        return pl.DataFrame(data, schema=cls.polars_schema())
