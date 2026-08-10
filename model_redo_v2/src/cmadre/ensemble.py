"""Leakage-safe non-negative stacking of out-of-fold distribution predictions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import nnls

from .labels import LabelIntervals, interval_midpoint
from .models.base import DistributionPrediction


@dataclass
class NonNegativeStacker:
    model_names: list[str]
    censored_weight: float = 0.25
    fit_transform: str = "log1p"
    weights_: np.ndarray | None = None

    def fit(
        self,
        predictions: dict[str, DistributionPrediction],
        labels: LabelIntervals,
        sample_weight: np.ndarray | None = None,
    ) -> NonNegativeStacker:
        if set(predictions) != set(self.model_names):
            raise ValueError("stacking predictions do not match configured model names")
        design = np.column_stack([predictions[name].q50 for name in self.model_names])
        target = interval_midpoint(labels)
        if self.fit_transform == "log1p":
            design = np.log1p(np.maximum(design, 0))
            target = np.log1p(np.maximum(target, 0))
        elif self.fit_transform != "identity":
            raise ValueError("fit_transform must be 'log1p' or 'identity'")
        valid = np.isfinite(design).all(axis=1) & np.isfinite(target)
        if valid.sum() < max(30, len(self.model_names) * 5):
            raise ValueError("insufficient valid OOF rows to fit stacking weights")
        row_weight = np.where(labels.exact, 1.0, float(self.censored_weight))[valid]
        if sample_weight is not None:
            supplied = np.asarray(sample_weight, dtype=float)
            if supplied.shape != (len(labels.lower),) or not np.isfinite(supplied).all():
                raise ValueError("stacking sample_weight must be finite and match labels")
            row_weight = row_weight * supplied[valid]
        root_weight = np.sqrt(row_weight)
        coefficients, _ = nnls(design[valid] * root_weight[:, None], target[valid] * root_weight)
        if coefficients.sum() <= 0:
            coefficients = np.ones(len(self.model_names), dtype=float)
        self.weights_ = coefficients / coefficients.sum()
        return self

    def predict(self, predictions: dict[str, DistributionPrediction]) -> DistributionPrediction:
        if self.weights_ is None:
            raise RuntimeError("stacker is not fitted")
        if set(predictions) != set(self.model_names):
            raise ValueError("prediction set differs from fitted stacker")
        q10 = sum(weight * predictions[name].q10 for weight, name in zip(self.weights_, self.model_names))
        q50 = sum(weight * predictions[name].q50 for weight, name in zip(self.weights_, self.model_names))
        q90 = sum(weight * predictions[name].q90 for weight, name in zip(self.weights_, self.model_names))
        available_probability = [
            (weight, predictions[name].p_detected)
            for weight, name in zip(self.weights_, self.model_names)
            if predictions[name].p_detected is not None
        ]
        p_detected = None
        if available_probability:
            probability_weight = sum(weight for weight, _ in available_probability)
            p_detected = (
                sum(weight * probability for weight, probability in available_probability)
                / probability_weight
            )
        return DistributionPrediction(
            q10=q10,
            q50=q50,
            q90=q90,
            p_detected=p_detected,
            extra={"stacking_weights": dict(zip(self.model_names, self.weights_.tolist()))},
        )

    def save(self, path: str | Path) -> None:
        if self.weights_ is None:
            raise RuntimeError("stacker is not fitted")
        Path(path).write_text(
            json.dumps(
                {
                    "model_names": self.model_names,
                    "weights": dict(zip(self.model_names, self.weights_.tolist())),
                    "censored_weight": self.censored_weight,
                    "fit_transform": self.fit_transform,
                    "fit_target": "interval_midpoint_with_censored_downweighting",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> NonNegativeStacker:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        result = cls(
            model_names=list(payload["model_names"]),
            censored_weight=float(payload["censored_weight"]),
            fit_transform=str(payload.get("fit_transform", "identity")),
        )
        result.weights_ = np.asarray([payload["weights"][name] for name in result.model_names], dtype=float)
        return result
