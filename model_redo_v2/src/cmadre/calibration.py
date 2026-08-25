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
    transform_name: str = "identity"
    adjustment_: float | None = None
    calibration_rows_: int = 0

    def _forward(self, values: np.ndarray) -> np.ndarray:
        if self.transform_name == "identity":
            return values
        if self.transform_name == "log1p":
            return np.log1p(np.maximum(values, 0.0))
        raise ValueError("CQR transform_name must be 'identity' or 'log1p'")

    def _inverse(self, values: np.ndarray) -> np.ndarray:
        if self.transform_name == "identity":
            return values
        if self.transform_name == "log1p":
            return np.expm1(values)
        raise ValueError("CQR transform_name must be 'identity' or 'log1p'")

    def fit(self, prediction: DistributionPrediction, labels: LabelIntervals) -> CQRCalibrator:
        exact = labels.exact & np.isfinite(labels.lower)
        self.calibration_rows_ = int(exact.sum())
        if self.calibration_rows_ < 30:
            raise ValueError("CQR requires at least 30 exact calibration observations")
        y = self._forward(labels.lower[exact])
        q10 = self._forward(prediction.q10[exact])
        q90 = self._forward(prediction.q90[exact])
        scores = np.maximum.reduce(
            [q10 - y, y - q90, np.zeros(self.calibration_rows_)]
        )
        level = min(np.ceil((self.calibration_rows_ + 1) * (1.0 - self.alpha)) / self.calibration_rows_, 1.0)
        self.adjustment_ = float(np.quantile(scores, level, method="higher"))
        return self

    def transform(self, prediction: DistributionPrediction) -> DistributionPrediction:
        if self.adjustment_ is None:
            raise RuntimeError("calibrator is not fitted")
        calibrated_q10 = self._inverse(self._forward(prediction.q10) - self.adjustment_)
        calibrated_q90 = self._inverse(self._forward(prediction.q90) + self.adjustment_)
        return DistributionPrediction(
            q10=np.maximum(calibrated_q10, 0),
            q50=prediction.q50,
            q90=np.maximum(calibrated_q90, prediction.q90),
            p_detected=prediction.p_detected,
            extra={
                **(prediction.extra or {}),
                "cqr_adjustment": self.adjustment_,
                "cqr_alpha": self.alpha,
                "cqr_transform": self.transform_name,
            },
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
                    "transform": self.transform_name,
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
        result = cls(
            alpha=float(payload["alpha"]),
            transform_name=str(payload.get("transform", "identity")),
        )
        result.adjustment_ = float(payload["adjustment"])
        result.calibration_rows_ = int(payload["calibration_rows"])
        return result
