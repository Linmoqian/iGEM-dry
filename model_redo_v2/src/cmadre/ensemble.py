"""Leakage-safe non-negative stacking of out-of-fold distribution predictions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, nnls

from .labels import LabelIntervals, interval_midpoint
from .models.base import DistributionPrediction


@dataclass
class NonNegativeStacker:
    model_names: list[str]
    censored_weight: float = 0.25
    fit_transform: str = "log1p"
    objective: str = "median_nnls"
    quantile_loss_weight: float = 0.25
    width_penalty: float = 0.05
    max_log_width: float = 4.0
    l2_penalty: float = 0.01
    weights_: np.ndarray | None = None

    def _row_weight(
        self, labels: LabelIntervals, sample_weight: np.ndarray | None
    ) -> np.ndarray:
        row_weight = np.where(labels.exact, 1.0, float(self.censored_weight)).astype(float)
        if sample_weight is not None:
            supplied = np.asarray(sample_weight, dtype=float)
            if supplied.shape != (len(labels.lower),) or not np.isfinite(supplied).all():
                raise ValueError("stacking sample_weight must be finite and match labels")
            row_weight *= supplied
        return row_weight

    def _fit_median_nnls(
        self,
        predictions: dict[str, DistributionPrediction],
        labels: LabelIntervals,
        sample_weight: np.ndarray | None,
    ) -> np.ndarray:
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
        root_weight = np.sqrt(self._row_weight(labels, sample_weight)[valid])
        coefficients, _ = nnls(design[valid] * root_weight[:, None], target[valid] * root_weight)
        if coefficients.sum() <= 0:
            coefficients = np.ones(len(self.model_names), dtype=float)
        return coefficients / coefficients.sum()

    @staticmethod
    def _pinball(residual: np.ndarray, quantile: float) -> np.ndarray:
        return np.maximum(quantile * residual, (quantile - 1.0) * residual)

    def _fit_distributional(
        self,
        predictions: dict[str, DistributionPrediction],
        labels: LabelIntervals,
        sample_weight: np.ndarray | None,
    ) -> np.ndarray:
        cubes = {
            quantile: np.column_stack(
                [getattr(predictions[name], quantile) for name in self.model_names]
            )
            for quantile in ("q10", "q50", "q90")
        }
        finite = np.isfinite(labels.lower) & np.isfinite(labels.upper)
        for cube in cubes.values():
            finite &= np.isfinite(cube).all(axis=1)
        if finite.sum() < max(30, len(self.model_names) * 5):
            raise ValueError("insufficient finite OOF distributions to fit stacking weights")

        lower = np.log1p(np.maximum(labels.lower[finite], 0.0))
        upper = np.log1p(np.maximum(labels.upper[finite], 0.0))
        exact = labels.exact[finite]
        row_weight = self._row_weight(labels, sample_weight)[finite]
        row_weight /= max(row_weight.mean(), 1e-12)
        selected_cubes = {name: values[finite] for name, values in cubes.items()}
        model_count = len(self.model_names)
        uniform = np.full(model_count, 1.0 / model_count)

        def loss(weights: np.ndarray) -> float:
            # Blend in the original concentration space, exactly as inference does,
            # then evaluate on the stable log1p scale.
            q10 = np.log1p(np.maximum(selected_cubes["q10"] @ weights, 0.0))
            q50 = np.log1p(np.maximum(selected_cubes["q50"] @ weights, 0.0))
            q90 = np.log1p(np.maximum(selected_cubes["q90"] @ weights, 0.0))

            point_distance = np.maximum.reduce([lower - q50, q50 - upper, np.zeros_like(q50)])
            point_loss = np.average(np.square(point_distance), weights=row_weight)

            quantile_loss = 0.0
            if exact.any():
                exact_weight = row_weight[exact]
                y = lower[exact]
                q10_loss = self._pinball(y - q10[exact], 0.1)
                q90_loss = self._pinball(y - q90[exact], 0.9)
                quantile_loss += np.average(q10_loss + q90_loss, weights=exact_weight)
            censored = ~exact
            if censored.any():
                censored_weight = row_weight[censored]
                incompatible = np.maximum(q10[censored] - upper[censored], 0.0) + np.maximum(
                    lower[censored] - q90[censored], 0.0
                )
                quantile_loss += np.average(incompatible, weights=censored_weight)

            log_width = np.maximum(q90 - q10, 0.0)
            excessive_width = np.maximum(log_width - float(self.max_log_width), 0.0)
            width_loss = np.average(np.square(excessive_width), weights=row_weight)
            regularization = np.square(weights - uniform).sum()
            return float(
                point_loss
                + float(self.quantile_loss_weight) * quantile_loss
                + float(self.width_penalty) * width_loss
                + float(self.l2_penalty) * regularization
            )

        starts = [uniform, self._fit_median_nnls(predictions, labels, sample_weight)]
        starts.extend(np.eye(model_count))
        best_weights = None
        best_loss = np.inf
        constraints = {"type": "eq", "fun": lambda value: float(value.sum() - 1.0)}
        bounds = [(0.0, 1.0)] * model_count
        for start in starts:
            start_loss = loss(np.asarray(start, dtype=float))
            if np.isfinite(start_loss) and start_loss < best_loss:
                best_weights = np.asarray(start, dtype=float)
                best_loss = start_loss
            result = minimize(
                loss,
                np.asarray(start, dtype=float),
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 500, "ftol": 1e-10},
            )
            if result.success and np.isfinite(result.fun) and result.fun < best_loss:
                best_weights = np.asarray(result.x, dtype=float)
                best_loss = float(result.fun)
        if best_weights is None:
            raise RuntimeError("distributional stacking optimization failed")
        weights = np.clip(best_weights, 0.0, 1.0)
        return weights / weights.sum()

    def fit(
        self,
        predictions: dict[str, DistributionPrediction],
        labels: LabelIntervals,
        sample_weight: np.ndarray | None = None,
    ) -> NonNegativeStacker:
        if set(predictions) != set(self.model_names):
            raise ValueError("stacking predictions do not match configured model names")
        if self.objective == "median_nnls":
            self.weights_ = self._fit_median_nnls(predictions, labels, sample_weight)
        elif self.objective == "distributional":
            self.weights_ = self._fit_distributional(predictions, labels, sample_weight)
        else:
            raise ValueError("stacking objective must be 'median_nnls' or 'distributional'")
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
                    "objective": self.objective,
                    "quantile_loss_weight": self.quantile_loss_weight,
                    "width_penalty": self.width_penalty,
                    "max_log_width": self.max_log_width,
                    "l2_penalty": self.l2_penalty,
                    "fit_target": (
                        "interval_midpoint_with_censored_downweighting"
                        if self.objective == "median_nnls"
                        else "distributional_interval_objective"
                    ),
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
            objective=str(payload.get("objective", "median_nnls")),
            quantile_loss_weight=float(payload.get("quantile_loss_weight", 0.25)),
            width_penalty=float(payload.get("width_penalty", 0.05)),
            max_log_width=float(payload.get("max_log_width", 4.0)),
            l2_penalty=float(payload.get("l2_penalty", 0.01)),
        )
        result.weights_ = np.asarray([payload["weights"][name] for name in result.model_names], dtype=float)
        return result
