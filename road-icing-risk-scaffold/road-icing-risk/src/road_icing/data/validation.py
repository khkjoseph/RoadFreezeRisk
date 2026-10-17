"""Validate normalized model table, not competition-specific raw field names."""
from __future__ import annotations

import pandas as pd

REQUIRED = ("station_id", "timestamp")


def read_table(path: str) -> pd.DataFrame:
    if path.lower().endswith(".parquet"):
        return pd.read_parquet(path)
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    raise ValueError("Expected a normalized .parquet or .csv file")


def validate_model_table(df: pd.DataFrame) -> dict:
    missing = [col for col in REQUIRED if col not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")
    if "road_surface_temp_c" not in df and "road_state" not in df and "is_ice" not in df:
        raise ValueError("At least one of road_surface_temp_c / road_state / is_ice is required")
    dt = pd.to_datetime(df["timestamp"], errors="coerce")
    report = {
        "rows": int(len(df)),
        "stations": int(df["station_id"].nunique(dropna=True)),
        "null_station_id": int(df["station_id"].isna().sum()),
        "invalid_timestamp": int(dt.isna().sum()),
        "duplicate_station_timestamp": int(pd.DataFrame({"s": df["station_id"], "t": dt}).duplicated().sum()),
        "missing_by_column": {str(k): int(v) for k, v in df.isna().sum().items()},
    }
    if "road_state" in df:
        report["road_state_counts"] = {str(k): int(v) for k, v in
                                       df["road_state"].value_counts(dropna=False).items()}
    return report
