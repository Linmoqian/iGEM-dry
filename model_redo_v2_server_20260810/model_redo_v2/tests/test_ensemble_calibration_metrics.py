from __future__ import annotations

import numpy as np
import pandas as pd

from cmadre.calibration import CQRCalibrator
from cmadre.ensemble import NonNegativeStacker
from cmadre.labels import LabelIntervals
from cmadre.metrics import evaluate_predictions
from cmadre.models.base import DistributionPrediction


def _exact_labels(values: np.ndarray) -> LabelIntervals:
    n = len(values)
    return LabelIntervals(
        lower=values.copy(),
        upper=values.copy(),
        exact=np.ones(n, dtype=bool),
        detected=values > 0,
        valid=np.ones(n, dtype=bool),
        exclusion_reason=np.full(n, "", dtype=object),
        limit_source=np.full(n, "", dtype=object),
    )


def test_stacker_prefers_better_model_and_cqr_expands_interval(tmp_path) -> None:
    y = np.linspace(0.1, 10, 100)
    labels = _exact_labels(y)
    good = DistributionPrediction(q10=y * 0.8, q50=y, q90=y * 1.2)
    bad = DistributionPrediction(q10=y * 0 + 20, q50=y * 0 + 25, q90=y * 0 + 30)
    stacker = NonNegativeStacker(["good", "bad"]).fit({"good": good, "bad": bad}, labels)
    assert stacker.weights_[0] > 0.99
    stacked = stacker.predict({"good": good, "bad": bad})
    narrow = DistributionPrediction(q10=y, q50=y, q90=y)
    shifted_labels = _exact_labels(y + 1)
    calibrated = CQRCalibrator(alpha=0.2).fit(narrow, shifted_labels).transform(stacked)
    assert np.all(calibrated.q10 <= stacked.q10)
    assert np.all(calibrated.q90 >= stacked.q90)
    stacker.save(tmp_path / "stacker.json")
    calibrator = CQRCalibrator(alpha=0.2).fit(narrow, shifted_labels)
    calibrator.save(tmp_path / "calibrator.json")
    assert np.allclose(NonNegativeStacker.load(tmp_path / "stacker.json").weights_, stacker.weights_)
    assert CQRCalibrator.load(tmp_path / "calibrator.json").adjustment_ == calibrator.adjustment_


def test_metrics_report_exact_and_source_macro() -> None:
    y = np.array([0.1, 0.2, 1.0, 2.0])
    labels = _exact_labels(y)
    prediction = DistributionPrediction(q10=y * 0.8, q50=y * 1.1, q90=y * 1.3)
    metadata = pd.DataFrame({"source_group": ["a", "a", "b", "b"]})
    metrics = evaluate_predictions(prediction, labels, metadata, thresholds=[0.5])
    assert metrics["point"]["exact_rows"] == 4
    assert metrics["source_macro_log1p_mae"] is not None
    assert metrics["risk_thresholds"]["0.5"]["known_rows"] == 4
