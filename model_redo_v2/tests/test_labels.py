from __future__ import annotations

import numpy as np
import pandas as pd

from cmadre.labels import build_label_intervals, interval_midpoint


def test_exact_censored_raw_limit_and_exclusions() -> None:
    frame = pd.DataFrame(
        {
            "target_ug_l": [1.2, np.nan, np.nan, -0.1, np.nan],
            "target_model_ug_l": [1.2, 0.25, 0.4, -0.1, np.nan],
            "is_censored": [0, 1, 1, 0, 1],
            "censor_limit_ug_l": [np.nan, 0.5, np.nan, np.nan, np.nan],
            "detection_limit_ug_l": [np.nan] * 5,
            "reporting_limit_ug_l": [np.nan] * 5,
            "target_raw": ["1.2", "<0.5", "< 0.8", "-0.1", "ND"],
            "target_quality_flag": ["", "", "", "negative_excluded", ""],
            "detected": [1, 0, 0, 0, 0],
        }
    )
    labels = build_label_intervals(frame)
    assert labels.valid.tolist() == [True, True, True, False, False]
    assert labels.exact.tolist() == [True, False, False, False, False]
    assert labels.lower[:3].tolist() == [1.2, 0.0, 0.0]
    assert labels.upper[:3].tolist() == [1.2, 0.5, 0.8]
    assert labels.limit_source[:3].tolist() == ["", "censor_limit_ug_l", "target_raw"]
    np.testing.assert_allclose(interval_midpoint(labels)[:3], [1.2, 0.25, 0.4])


def test_no_valid_negative_or_reversed_interval() -> None:
    frame = pd.DataFrame(
        {
            "target_ug_l": [0.0, 2.0],
            "target_model_ug_l": [0.0, 2.0],
            "is_censored": [0, 0],
            "target_quality_flag": ["", ""],
        }
    )
    labels = build_label_intervals(frame)
    assert labels.valid.all()
    assert np.all(labels.lower >= 0)
    assert np.all(labels.upper >= labels.lower)
