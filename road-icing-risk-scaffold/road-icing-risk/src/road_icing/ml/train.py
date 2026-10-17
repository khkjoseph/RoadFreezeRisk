"""Minimal honest baseline: station-disjoint test, no target leakage, no fake results."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score, mean_absolute_error, mean_squared_error, precision_score, recall_score
from sklearn.pipeline import Pipeline

from road_icing.data.validation import read_table, validate_model_table
from road_icing.ml.features import select_features
from road_icing.ml.split import station_split, assert_disjoint_stations


def _read_config(path: str) -> dict:
    with open(path, encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    if not isinstance(data, dict):
        raise ValueError("Invalid experiment YAML")
    return data


def _attach_label(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "is_ice" not in df and "road_state" in df:
        valid = df["road_state"].notna()
        df["is_ice"] = np.nan
        df.loc[valid, "is_ice"] = df.loc[valid, "road_state"].astype(str).str.strip().str.casefold().eq("ice").astype(int)
    if "is_ice" in df:
        distinct = set(df["is_ice"].dropna().unique().tolist())
        if not distinct.issubset({0, 1, 0.0, 1.0, False, True}):
            raise ValueError("is_ice must be binary 0/1. Verify actual road-state labels")
    return df


def _task(task: str, train: pd.DataFrame, val: pd.DataFrame, holdout: pd.DataFrame,
          features: list[str], seed: int, output: Path) -> dict:
    target = "road_surface_temp_c" if task == "regression" else "is_ice"
    if target not in train.columns:
        return {"status": "skipped", "reason": f"missing target column {target}"}
    tr = train[train[target].notna()].copy()
    va = val[val[target].notna()].copy()
    ho = holdout[holdout[target].notna()].copy()
    if not len(tr) or not len(va) or not len(ho):
        return {"status": "skipped", "reason": "missing labeled examples for one split"}
    if task == "classification" and tr[target].nunique() < 2:
        return {"status": "skipped", "reason": "train split contains only one label"}
    estimator = (HistGradientBoostingRegressor(random_state=seed) if task == "regression" else
                 HistGradientBoostingClassifier(random_state=seed))
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("estimator", estimator),
    ])
    pipeline.fit(tr[features], tr[target].astype(float))

    def scores(ds: pd.DataFrame) -> dict:
        y = ds[target].astype(float).to_numpy()
        pred = pipeline.predict(ds[features])
        if task == "regression":
            return {"n": len(ds), "mae": float(mean_absolute_error(y, pred)),
                    "rmse": float(np.sqrt(mean_squared_error(y, pred))),
                    "bias_pred_minus_true": float(np.mean(pred-y))}
        return {"n": len(ds), "precision": float(precision_score(y, pred, zero_division=0)),
                "recall": float(recall_score(y, pred, zero_division=0)),
                "f1": float(f1_score(y, pred, zero_division=0)),
                "positives": int(y.sum())}

    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output / f"baseline_{task}.joblib")
    return {"status": "trained", "validation": scores(va), "holdout": scores(ho)}


def run_training(table: str, config_path: str, output: str = "models", report_path: str = "reports/baseline_metrics.json") -> dict:
    cfg = _read_config(config_path)
    df = _attach_label(read_table(table))
    validity = validate_model_table(df)
    if validity["invalid_timestamp"] or validity["null_station_id"] or validity["duplicate_station_timestamp"]:
        raise ValueError(f"Data validation failed: {validity}. Repair normalization first")
    features = select_features(df, cfg["feature_candidates"])
    train, val, holdout = station_split(df, cfg["holdout_station_ids"],
                                        cfg.get("validation_station_fraction", 0.2), cfg.get("seed", 42))
    assert_disjoint_stations(train, val, holdout)
    out_dir = Path(output)
    metrics = {
        "note": "Holdout metrics are diagnostic only. Do not tune repeatedly using held-out stations.",
        "features": features,
        "split_station_counts": {"train": int(train.station_id.nunique()),
                                 "validation": int(val.station_id.nunique()),
                                 "holdout": int(holdout.station_id.nunique())},
        "tasks": {
            task: _task(task, train, val, holdout, features, cfg.get("seed", 42), out_dir)
            for task in ("regression", "classification")
        },
    }
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics
