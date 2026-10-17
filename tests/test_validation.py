import pandas as pd
import pytest
from road_icing.data.validation import validate_model_table


def test_detect_duplicates():
    df = pd.DataFrame({"station_id": [1, 1], "timestamp": ["2025-01-01", "2025-01-01"],
                       "road_state": ["Ice", "Dry"]})
    assert validate_model_table(df)["duplicate_station_timestamp"] == 1


def test_missing_columns():
    with pytest.raises(ValueError):
        validate_model_table(pd.DataFrame({"road_state": ["Ice"]}))
