"""Interpretable detection-plus-positive-concentration hurdle model."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..labels import LabelIntervals
from .base import CensoredRegressor, DistributionPrediction


class CatBoostHurdleRegressor(CensoredRegressor):
    name = "catboost_hurdle"

    def __init__(self, params: dict, seed: int = 42):
        self.params = dict(params)
        self.seed = int(seed)
        self.classifier = None
        self.positive_models: dict[float, object] = {}
        self.feature_names: list[str] | None = None

    @staticmethod
    def _imports():
        try:
            from catboost import CatBoostClassifier, CatBoostRegressor
        except ImportError as exc:
            raise ImportError("catboost is required for model 'catboost_hurdle'") from exc
        return CatBoostClassifier, CatBoostRegressor

    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> CatBoostHurdleRegressor:
        CatBoostClassifier, CatBoostRegressor = self._imports()
        self.feature_names = list(X.columns)
        detection = labels.detected.astype(int)
        if len(np.unique(detection)) < 2:
            raise ValueError("hurdle classifier requires both detected and non-detected training samples")
        common = {
            "iterations": int(self.params.get("iterations", 1000)),
            "depth": int(self.params.get("depth", 7)),
            "learning_rate": float(self.params.get("learning_rate", 0.04)),
            "l2_leaf_reg": float(self.params.get("l2_leaf_reg", 5.0)),
            "random_seed": self.seed,
            "task_type": self.params.get("task_type", "CPU"),
            "allow_writing_files": False,
            "verbose": False,
        }
        self.classifier = CatBoostClassifier(loss_function="Logloss", eval_metric="BrierScore", **common)
        classifier_kwargs = {"sample_weight": sample_weight, "verbose": False}
        if (
            X_validation is not None
            and validation_labels is not None
            and len(np.unique(validation_labels.detected)) > 1
        ):
            classifier_kwargs.update(
                {
                    "eval_set": (X_validation, validation_labels.detected.astype(int)),
                    "early_stopping_rounds": int(self.params.get("early_stopping_rounds", 80)),
                    "use_best_model": True,
                }
            )
        self.classifier.fit(X, detection, **classifier_kwargs)

        positive = labels.exact & labels.detected & (labels.lower > 0)
        if positive.sum() < 30:
            raise ValueError("hurdle positive regression requires at least 30 exact positive samples")
        positive_weight = None if sample_weight is None else np.asarray(sample_weight)[positive]
        positive_validation = None
        if X_validation is not None and validation_labels is not None:
            positive_validation = (
                validation_labels.exact & validation_labels.detected & (validation_labels.lower > 0)
            )
        for quantile in (0.1, 0.5, 0.9):
            model = CatBoostRegressor(
                loss_function=f"Quantile:alpha={quantile}",
                eval_metric=f"Quantile:alpha={quantile}",
                **common,
            )
            kwargs = {"sample_weight": positive_weight, "verbose": False}
            if positive_validation is not None and positive_validation.sum() >= 10:
                kwargs.update(
                    {
                        "eval_set": (
                            X_validation.iloc[np.flatnonzero(positive_validation)],
                            np.log1p(validation_labels.lower[positive_validation]),
                        ),
                        "early_stopping_rounds": int(self.params.get("early_stopping_rounds", 80)),
                        "use_best_model": True,
                    }
                )
            model.fit(X.iloc[np.flatnonzero(positive)], np.log1p(labels.lower[positive]), **kwargs)
            self.positive_models[quantile] = model
        return self

    @staticmethod
    def _conditional_quantile(
        probability: np.ndarray, q10: np.ndarray, q50: np.ndarray, q90: np.ndarray
    ) -> np.ndarray:
        probability = np.clip(probability, 0, 1)
        result = np.empty_like(probability, dtype=float)
        low = probability <= 0.1
        mid_low = (probability > 0.1) & (probability <= 0.5)
        mid_high = (probability > 0.5) & (probability <= 0.9)
        high = probability > 0.9
        result[low] = q10[low] * probability[low] / 0.1
        result[mid_low] = q10[mid_low] + (q50[mid_low] - q10[mid_low]) * (probability[mid_low] - 0.1) / 0.4
        result[mid_high] = (
            q50[mid_high] + (q90[mid_high] - q50[mid_high]) * (probability[mid_high] - 0.5) / 0.4
        )
        result[high] = q90[high] * np.exp((probability[high] - 0.9) / 0.1 * np.log(2.0))
        return result

    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        if self.classifier is None or set(self.positive_models) != {0.1, 0.5, 0.9}:
            raise RuntimeError("model is not fitted")
        if list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted hurdle model")
        p_detected = np.asarray(self.classifier.predict_proba(X)[:, 1], dtype=float)
        conditional = {
            q: np.maximum(np.expm1(self.positive_models[q].predict(X)), 0) for q in (0.1, 0.5, 0.9)
        }
        unconditional = []
        for probability in (0.1, 0.5, 0.9):
            is_mass_at_zero = probability <= (1.0 - p_detected)
            conditional_probability = (probability - (1.0 - p_detected)) / np.maximum(p_detected, 1e-8)
            values = self._conditional_quantile(
                conditional_probability, conditional[0.1], conditional[0.5], conditional[0.9]
            )
            values[is_mass_at_zero] = 0.0
            unconditional.append(values)
        return DistributionPrediction(
            q10=unconditional[0], q50=unconditional[1], q90=unconditional[2], p_detected=p_detected
        )
