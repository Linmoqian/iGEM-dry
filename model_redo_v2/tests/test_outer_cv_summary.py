from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest


def test_outer_cv_aggregate_reports_mean_and_dispersion() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_outer_cv.py"
    spec = importlib.util.spec_from_file_location("run_outer_cv", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    summary = module._aggregate(
        pd.DataFrame(
            {
                "repeat": [0, 0],
                "test_fold": [0, 1],
                "run_dir": ["a", "b"],
                "log1p_mae": [0.2, 0.4],
            }
        )
    )
    assert summary["fold_runs"] == 2
    assert summary["numeric"]["log1p_mae"]["mean"] == pytest.approx(0.3)
    assert summary["numeric"]["log1p_mae"]["std"] > 0
