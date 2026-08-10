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
    assert NonNegativeStacker.load(tmp_path / "stacker.json").fit_transform == "log1p"
    assert CQRCalibrator.load(tmp_path / "calibrator.json").adjustment_ == calibrator.adjustment_


def test_log_cqr_is_multiplicative_and_round_trips(tmp_path) -> None:
    y = np.geomspace(0.1, 1000.0, 100)
    labels = _exact_labels(y * 2.0)
    narrow = DistributionPrediction(q10=y, q50=y, q90=y)
    calibrator = CQRCalibrator(alpha=0.2, transform_name="log1p").fit(narrow, labels)
    calibrated = calibrator.transform(narrow)
    assert calibrated.q10.min() >= 0
    assert np.all(calibrated.q90 >= narrow.q90)
    # Log calibration expands high concentrations more in raw units, matching
    # multiplicative error rather than imposing one global ug/L adjustment.
    raw_expansion = calibrated.q90 - narrow.q90
    assert raw_expansion[-1] > 100 * raw_expansion[0]
    calibrator.save(tmp_path / "log_calibrator.json")
    loaded = CQRCalibrator.load(tmp_path / "log_calibrator.json")
    assert loaded.transform_name == "log1p"
    assert np.allclose(loaded.transform(narrow).q90, calibrated.q90)


def test_metrics_report_exact_and_source_macro() -> None:
    y = np.array([0.1, 0.2, 1.0, 2.0])
    labels = _exact_labels(y)
    prediction = DistributionPrediction(q10=y * 0.8, q50=y * 1.1, q90=y * 1.3)
    metadata = pd.DataFrame({"source_group": ["a", "a", "b", "b"]})
    metrics = evaluate_predictions(prediction, labels, metadata, thresholds=[0.5])
    assert metrics["point"]["exact_rows"] == 4
    assert metrics["source_macro_log1p_mae"] is not None
    assert metrics["risk_thresholds"]["0.5"]["known_rows"] == 4


def test_metrics_report_tail_underprediction() -> None:
    y = np.arange(1.0, 101.0)
    labels = _exact_labels(y)
    prediction = DistributionPrediction(q10=y * 0.1, q50=y * 0.5, q90=y)
    metrics = evaluate_predictions(prediction, labels)
    tail = metrics["tail_diagnostics"]["q90"]
    assert tail["rows"] >= 10
    assert tail["underprediction_rate"] == 1.0
    assert tail["median_prediction_ug_l"] < tail["median_true_ug_l"]


def test_distributional_stacker_rejects_pathological_width() -> None:
    y = np.linspace(0.1, 10, 100)
    labels = _exact_labels(y)
    stable = DistributionPrediction(q10=y * 0.5, q50=y, q90=y * 2.0)
    pathological = DistributionPrediction(q10=y * 0.9, q50=y, q90=np.full_like(y, 1e18))
    stacker = NonNegativeStacker(
        ["stable", "pathological"],
        objective="distributional",
        width_penalty=0.1,
        max_log_width=4.0,
    ).fit({"stable": stable, "pathological": pathological}, labels)
    assert stacker.weights_[0] > 0.99


def test_log_blend_matches_training_space_and_round_trips(tmp_path) -> None:
    low = DistributionPrediction(
        q10=np.array([1.0]), q50=np.array([1.0]), q90=np.array([1.0])
    )
    high = DistributionPrediction(
        q10=np.array([99.0]), q50=np.array([99.0]), q90=np.array([99.0])
    )
    stacker = NonNegativeStacker(
        ["low", "high"], blend_transform="log1p", weights_=np.array([0.5, 0.5])
    )
    prediction = stacker.predict({"low": low, "high": high})
    expected = np.expm1((np.log1p(1.0) + np.log1p(99.0)) / 2.0)
    assert np.allclose(prediction.q50, expected)
    assert prediction.q50[0] < 50.0
    stacker.save(tmp_path / "log_stacker.json")
    loaded = NonNegativeStacker.load(tmp_path / "log_stacker.json")
    assert loaded.blend_transform == "log1p"
    assert np.allclose(loaded.predict({"low": low, "high": high}).q50, prediction.q50)
