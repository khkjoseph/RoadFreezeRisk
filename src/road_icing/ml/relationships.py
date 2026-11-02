"""Validation-only associations; these describe relationships, not causal effects."""

from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance


def relationship_report(model, frame, features, target, task, seed):
    x = frame[features]
    y = frame[target].astype(float)
    score = model.predict_proba(x)[:, 1] if task == "classification" else model.predict(x)
    scoring = "neg_brier_score" if task == "classification" else "neg_mean_absolute_error"
    importance = permutation_importance(
        model,
        x,
        y,
        scoring=scoring,
        n_repeats=5,
        random_state=seed,
    )

    def correlation(a, b):
        valid = a.notna() & b.notna()
        if valid.sum() < 3 or a[valid].nunique() < 2 or b[valid].nunique() < 2:
            return None
        value = a[valid].corr(b[valid], method="spearman")
        return float(value) if np.isfinite(value) else None

    predicted = pd.Series(score, index=frame.index)
    variables = {}
    for i, feature in enumerate(features):
        values = x[feature]
        bins = []
        if values.nunique() > 1:
            for interval, indices in values.groupby(
                pd.qcut(values, q=min(4, values.nunique()), duplicates="drop"),
                observed=True,
            ).groups.items():
                bins.append(
                    {
                        "range": str(interval),
                        "n": len(indices),
                        "observed_target_mean": float(y.loc[indices].mean()),
                        "predicted_mean": float(predicted.loc[indices].mean()),
                    }
                )
        variables[feature] = {
            "n_observed": int(values.notna().sum()),
            "spearman_with_target": correlation(values, y),
            "spearman_with_prediction": correlation(values, predicted),
            "permutation_score_decrease": float(importance.importances_mean[i]),
            "permutation_std": float(importance.importances_std[i]),
            "bins": bins,
        }
    pairs = []
    for a, b in combinations(features, 2):
        valid = x[a].notna() & x[b].notna()
        groups = []
        # Medians are descriptive validation summaries, never training inputs.
        for high_a in (False, True):
            for high_b in (False, True):
                mask = valid & ((x[a] > x[a].median()) == high_a)
                mask &= (x[b] > x[b].median()) == high_b
                if mask.any():
                    groups.append(
                        {
                            "above_median": [high_a, high_b],
                            "n": int(mask.sum()),
                            "observed_target_mean": float(y[mask].mean()),
                            "predicted_mean": float(predicted[mask].mean()),
                        }
                    )
        pairs.append(
            {"features": [a, b], "spearman": correlation(x[a], x[b]), "joint_conditions": groups}
        )
    return {
        "scope": "validation stations only; associations are not causal; sparse bins are unstable",
        "importance_scoring": scoring,
        "variables": variables,
        "pairs": pairs,
    }
