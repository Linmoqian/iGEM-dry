"""GPU-capable XGBoost quantile experts with optional training-fold tail emphasis."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..labels import LabelIntervals, interval_midpoint
from .base import CensoredRegressor, DistributionPrediction

QUANTILES = (0.1, 0.5, 0.9)


class XGBoostQuantileRegressor(CensoredRegressor):
    """Three quantile boosters on log1p concentration.

    XGBoost's quantile objective does not accept interval labels. Censored rows
    therefore use a transparent midpoint proxy with reduced weight. The optional
    tail emphasis is computed from exact labels in the current training fold only;
    it creates a deliberately different expert for regime-aware stacking.
    """

    name = "xgb_quantile"

    def __init__(self, params: dict, seed: int = 42, name: str = "xgb_quantile"):
        self.params = dict(params)
        self.seed = int(seed)
        self.name = str(name)
        self.boosters: dict[float, object] = {}
        self.feature_names: list[str] | None = None
        self.tail_threshold_log_: float | None = None

    @staticmethod
    def _import_xgboost():
        try:
            import xgboost as xgb
        except ImportError as exc:
            raise ImportError("xgboost is required for quantile experts") from exc
        return xgb

    def _target_and_weight(
        self, labels: LabelIntervals, sample_weight: np.ndarray | None
    ) -> tuple[np.ndarray, np.ndarray]:
        target = np.log1p(interval_midpoint(labels))
        weight = np.where(labels.exact, 1.0, float(self.params.get("censored_weight", 0.25)))
        if sample_weight is not None:
            weight *= np.asarray(sample_weight, dtype=float)

        strength = float(self.params.get("tail_weight_strength", 0.0))
        exact_target = target[labels.exact & np.isfinite(target)]
        if strength > 0 and len(exact_target) >= 30:
            quantile = float(self.params.get("tail_quantile", 0.9))
            if not 0.5 <= quantile < 1.0:
                raise ValueError("tail_quantile must be in [0.5, 1)")
            threshold = float(np.quantile(exact_target, quantile))
            maximum = float(exact_target.max())
            denominator = max(maximum - threshold, 1e-8)
            severity = np.clip((target - threshold) / denominator, 0.0, 1.0)
            selected = labels.exact & (target >= threshold)
            weight[selected] *= 1.0 + strength * (0.25 + 0.75 * severity[selected])
            self.tail_threshold_log_ = threshold
        return target, weight

    def _matrix(self, X: pd.DataFrame, label=None, weight=None, ref=None):
        xgb = self._import_xgboost()
        if self.feature_names is not None and list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted XGBoost quantile model")
        return xgb.QuantileDMatrix(
            X,
            label=label,
            weight=weight,
            feature_names=list(X.columns),
            missing=np.nan,
            ref=ref,
        )

    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> XGBoostQuantileRegressor:
        xgb = self._import_xgboost()
        self.feature_names = list(X.columns)
        target, weight = self._target_and_weight(labels, sample_weight)
        dtrain = self._matrix(X, target.astype(np.float32), weight.astype(np.float32))
        validation = None
        if X_validation is not None and validation_labels is not None and len(X_validation):
            validation_target = np.log1p(interval_midpoint(validation_labels)).astype(np.float32)
            validation_weight = np.where(
                validation_labels.exact,
                1.0,
                float(self.params.get("censored_weight", 0.25)),
            ).astype(np.float32)
            validation = self._matrix(
                X_validation, validation_target, validation_weight, ref=dtrain
            )

        common = {
            "objective": "reg:quantileerror",
            "eval_metric": "quantile",
            "eta": float(self.params.get("learning_rate", 0.03)),
            "max_depth": int(self.params.get("max_depth", 6)),
            "min_child_weight": float(self.params.get("min_child_weight", 5.0)),
            "subsample": float(self.params.get("subsample", 0.85)),
            "colsample_bytree": float(self.params.get("colsample_bytree", 0.85)),
            "lambda": float(self.params.get("reg_lambda", 2.0)),
            "tree_method": self.params.get("tree_method", "hist"),
            "device": self.params.get("device", "cpu"),
            "seed": self.seed,
            "nthread": int(self.params.get("n_jobs", -1)),
        }
        for quantile in QUANTILES:
            params = {**common, "quantile_alpha": quantile}
            evaluations = [(dtrain, "train")]
            if validation is not None:
                evaluations.append((validation, "validation"))
            self.boosters[quantile] = xgb.train(
                params,
                dtrain,
                num_boost_round=int(self.params.get("num_boost_round", 1200)),
                evals=evaluations,
                early_stopping_rounds=(
                    int(self.params.get("early_stopping_rounds", 80))
                    if validation is not None
                    else None
                ),
                verbose_eval=False,
            )
        return self

    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        if set(self.boosters) != set(QUANTILES):
            raise RuntimeError("model is not fitted")
        xgb = self._import_xgboost()
        if list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted XGBoost quantile model")
        matrix = xgb.DMatrix(X, feature_names=list(X.columns), missing=np.nan)
        values = [
            np.maximum(np.expm1(np.asarray(self.boosters[q].predict(matrix), dtype=float)), 0.0)
            for q in QUANTILES
        ]
        return DistributionPrediction(
            q10=values[0],
            q50=values[1],
            q90=values[2],
            extra={
                "tail_threshold_log1p": self.tail_threshold_log_,
                "tail_weight_strength": float(self.params.get("tail_weight_strength", 0.0)),
            },
        )
