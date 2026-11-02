import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

from road_icing.ml.relationships import relationship_report
from road_icing.ml.train import _attach_label


def test_numeric_road_state_requires_verified_mapping():
    with pytest.raises(ValueError, match="Unmapped road_state"):
        _attach_label(pd.DataFrame({"road_state": [1, 12, 14]}))


def test_missing_label_is_not_non_ice():
    result = _attach_label(pd.DataFrame({"road_state": ["Ice", "Dry", None]}))
    assert result.is_ice.iloc[:2].tolist() == [1, 0]
    assert pd.isna(result.is_ice.iloc[2])


def test_relationships_constant_missing_and_joint_counts():
    # Small unit-test fixture, never used as training data or reported performance.
    frame = pd.DataFrame({"a": [1.0, 2.0, np.nan, 4.0], "b": [2.0] * 4, "is_ice": [0, 1, 0, 1]})
    model = DummyClassifier(strategy="prior").fit(frame[["a", "b"]], frame.is_ice)
    report = relationship_report(model, frame, ["a", "b"], "is_ice", "classification", 42)
    assert report["variables"]["b"]["spearman_with_target"] is None
    assert report["variables"]["a"]["n_observed"] == 3
    assert sum(g["n"] for g in report["pairs"][0]["joint_conditions"]) == 3
    assert report["variables"]["a"]["permutation_score_decrease"] == 0
