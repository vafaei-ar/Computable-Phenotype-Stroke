"""Regression checks for center-anchored six-month aggregation."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aggregation_sensitivity import evaluate


def test_semiannual_periods_are_anchored_to_first_calendar_quarter():
    months_1 = pd.period_range("2016-12", "2017-07", freq="M").astype(str)
    months_2 = pd.period_range("2017-01", "2017-08", freq="M").astype(str)
    df = pd.DataFrame(
        [
            {"center_id": center, "month": month, "definition_id": "D0",
             "phenotype_count": 9, "registry_count": 10}
            for center, months in [("1", months_1), ("2", months_2)]
            for month in months
        ]
    )
    result = evaluate(df)
    m1 = result[(result.center_id == "1") & (result.aggregation == "semiannual")].iloc[0]
    m2 = result[(result.center_id == "2") & (result.aggregation == "semiannual")].iloc[0]
    assert int(m1["periods"]) == 2
    assert int(m2["periods"]) == 2
    assert float(m1["MAE"]) == 4.0  # first Dec-Mar, then Apr-Jul: four months each
    assert float(m2["MAE"]) == 4.0  # first Jan-Jun, then Jul-Aug: six plus two months
    # Mean MAE happens to match, but the grouping boundary does not.
    assert float(m1["RMSE"]) == 4.0
    assert abs(float(m2["RMSE"]) - ((36 + 4) / 2) ** 0.5) < 1e-8


def test_reject_duplicate_center_month_definition():
    df = pd.DataFrame([{"center_id":"1", "month":"2017-01","definition_id":"D0",
                        "phenotype_count":1,"registry_count":1}] * 2)
    import pytest
    with pytest.raises(ValueError, match="Duplicate"):
        evaluate(df)
