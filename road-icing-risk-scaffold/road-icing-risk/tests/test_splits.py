import pandas as pd
import pytest
from road_icing.ml.split import assert_disjoint_stations, station_split
from road_icing.ml.features import select_features


def test_group_holdout():
    stations = [1, 2, 3, 4, 5, 100]
    df = pd.DataFrame([{"station_id": s, "timestamp": "2025-01-01"} for s in stations])
    train, val, holdout = station_split(df, [100], 0.25, 42)
    assert_disjoint_stations(train, val, holdout)
    assert set(holdout.station_id) == {100}


def test_missing_holdout_fails():
    with pytest.raises(ValueError):
        station_split(pd.DataFrame({"station_id": [1, 2]}), [999])


def test_leakage_guard():
    with pytest.raises(ValueError):
        select_features(pd.DataFrame({"road_surface_temp_c": [0.1], "air_temp_c": [1]}),
                        ["road_surface_temp_c", "air_temp_c"])
