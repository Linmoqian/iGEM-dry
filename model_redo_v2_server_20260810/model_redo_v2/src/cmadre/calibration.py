"""Exact-observation conformalized quantile calibration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .labels import LabelIntervals
from .models.base import DistributionPrediction


@dataclass
class CQRCalibrator:
    alpha: float = 0.2
    adjustment_: float | None = None
    calibration_rows_: int = 0

    def fit(self, prediction: DistributionPrediction, labels: LabelIntervals) -> CQRCalibrator:
        exact = labels.exact & np.isfinite(labels.lower)
        self.calibration_rows_ = int(exact.sum())
        if self.calibration_rows_ < 30:
            raise ValueError("CQR requires at least 30 exact calibration observations")
        y = labels.lower[exact]
        scores = np.maximum.reduce(
            [prediction.q10[exact] - y, y - prediction.q90[exact], np.zeros(self.calibration_rows_)]
        )
        level = min(np.ceil((self.calibration_rows_ + 1) * (1.0 - self.alpha)) / self.calibration_rows_, 1.0)
        self.adjustment_ = float(np.quantile(scores, level, method="higher"))
        return self

    def transform(self, prediction: DistributionPrediction) -> DistributionPrediction:
        if self.adjustment_ is None:
            raise RuntimeError("calibrator is not fitted")
        return DistributionPrediction(
            q10=np.maximum(prediction.q10 - self.adjustment_, 0),
            q50=prediction.q50,
            q90=prediction.q90 + self.adjustment_,
            p_detected=prediction.p_detected,
            extra={**(prediction.extra or {}), "cqr_adjustment": self.adjustment_, "cqr_alpha": self.alpha},
        )

    def save(self, path: str | Path) -> None:
        if self.adjustment_ is None:
            raise RuntimeError("calibrator is not fitted")
        Path(path).write_text(
            json.dumps(
                {
                    "alpha": self.alpha,
                    "adjustment": self.adjustment_,
                    "calibration_rows": self.calibration_rows_,
                    "scope": "exact_observations_only",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> CQRCalibrator:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        result = cls(alpha=float(payload["alpha"]))
        result.adjustment_ = float(payload["adjustment"])
        result.calibration_rows_ = int(payload["calibration_rows"])
        return result
