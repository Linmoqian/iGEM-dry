from __future__ import annotations

import numpy as np
import pandas as pd

from cmadre.ood import FeatureOODDetector


def test_ood_detector_flags_far_points_and_roundtrips(tmp_path) -> None:
    rng = np.random.default_rng(42)
    train = pd.DataFrame({"a": rng.normal(size=300), "b": rng.normal(size=300)})
    train.loc[::11, "b"] = np.nan
    detector = FeatureOODDetector(0.95).fit(train)
    probe = pd.DataFrame({"a": [0.0, 50.0], "b": [0.0, 50.0]})
    result = detector.predict(probe)
    assert not result.flag[0]
    assert result.flag[1]
    detector.save(tmp_path / "ood.pkl")
    restored = FeatureOODDetector.load(tmp_path / "ood.pkl").predict(probe)
    assert np.allclose(restored.score, result.score)
    assert np.array_equal(restored.flag, result.flag)
