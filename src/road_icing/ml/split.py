"""Station-based (not row-random) validation and competition holdout."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


def station_split(df: pd.DataFrame, holdout_station_ids: list, val_fraction: float = 0.2,
                  seed: int = 42):
    if "station_id" not in df:
        raise ValueError("station_id column required")
    sites = df["station_id"].astype(str)
    holdouts = {str(x) for x in holdout_station_ids}
    if not holdouts:
        raise ValueError("Explicit holdout_station_ids must be set and officially confirmed")
    holdout_mask = sites.isin(holdouts)
    observed = set(sites[holdout_mask])
    if not observed:
        raise ValueError("No configured holdout stations found in normalized dataset")
    available = df.loc[~holdout_mask]
    if available["station_id"].nunique() < 2:
        raise ValueError("Need at least two non-holdout stations for independent validation")
    splitter = GroupShuffleSplit(n_splits=1, test_size=val_fraction, random_state=seed)
    tr_idx, val_idx = next(splitter.split(available, groups=available["station_id"].astype(str)))
    return available.iloc[tr_idx].copy(), available.iloc[val_idx].copy(), df.loc[holdout_mask].copy()


def assert_disjoint_stations(*frames: pd.DataFrame) -> None:
    groups = [set(f["station_id"].astype(str)) for f in frames]
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            if groups[i] & groups[j]:
                raise AssertionError(f"Station leakage between splits {i} and {j}")
