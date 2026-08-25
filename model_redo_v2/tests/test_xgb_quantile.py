from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("xgboost")

from cmadre.labels import LabelIntervals
from cmadre.models.xgb_quantile import XGBoostQuantileRegressor


def _labels(values: np.ndarray) -> LabelIntervals:
    size = len(values)
    return LabelIntervals(
        lower=values,
        upper=values,
        exact=np.ones(size, dtype=bool),
        detected=values > 0,
        valid=np.ones(size, dtype=bool),
        exclusion_reason=np.full(size, "", dtype=object),
        limit_source=np.full(size, "", dtype=object),
    )


def test_xgb_quantile_tail_expert_is_finite_ordered_and_reloadable(tmp_path) -> None:
    rng = np.random.default_rng(42)
    X = pd.DataFrame(rng.normal(size=(120, 4)), columns=list("abcd"))
    y = np.maximum(np.exp(0.5 * X["a"].to_numpy() + rng.normal(0, 0.1, 120)) - 1, 0)
    model = XGBoostQuantileRegressor(
        {
            "num_boost_round": 20,
            "early_stopping_rounds": 5,
            "max_depth": 3,
            "tree_method": "hist",
            "device": "cpu",
            "tail_weight_strength": 2.0,
            "tail_quantile": 0.9,
        },
        seed=42,
        name="xgb_quantile_tail",
    ).fit(X.iloc[:90], _labels(y[:90]), X.iloc[90:], _labels(y[90:]))
    prediction = model.predict_distribution(X.iloc[90:])
    assert np.isfinite(prediction.q50).all()
    assert np.all(prediction.q10 <= prediction.q50)
    assert np.all(prediction.q50 <= prediction.q90)
    assert model.tail_threshold_log_ is not None
    artifact = tmp_path / "xgb_quantile_tail.pkl"
    model.save(artifact)
    reloaded = XGBoostQuantileRegressor.load(artifact)
    reloaded_prediction = reloaded.predict_distribution(X.iloc[90:])
    assert np.allclose(reloaded_prediction.q50, prediction.q50)
