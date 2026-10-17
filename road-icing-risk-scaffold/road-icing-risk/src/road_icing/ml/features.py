"""Explicit allowlist to avoid using unavailable RWIS target columns at inference."""
from __future__ import annotations

import pandas as pd

FORBIDDEN_FEATURES = {
    "road_surface_temp_c", "road_state", "is_ice", "station_id", "station_name",
    "timestamp", "label", "target", "ice_probability", "pred_road_surface_temp_c",
}


def select_features(df: pd.DataFrame, requested: list[str]) -> list[str]:
    forbidden = sorted(set(requested) & FORBIDDEN_FEATURES)
    if forbidden:
        raise ValueError(f"Forbidden target/ID/time features: {forbidden}")
    # Explicitly reject string columns: downstream estimator assumes numeric-only predictors.
    features = [col for col in requested if col in df.columns]
    if not features:
        raise ValueError("None of the candidate features exists in the normalized dataset")
    bad_dtype = [c for c in features if not (pd.api.types.is_numeric_dtype(df[c]) or
                                            pd.api.types.is_bool_dtype(df[c]))]
    if bad_dtype:
        raise TypeError(f"Non-numeric predictor columns require explicit encoding: {bad_dtype}")
    return features
