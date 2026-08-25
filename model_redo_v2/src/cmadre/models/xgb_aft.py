"""XGBoost accelerated-failure-time model applied to concentration intervals."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.special import expit, ndtr, ndtri

from ..labels import LabelIntervals
from .base import CensoredRegressor, DistributionPrediction


class XGBoostAFTRegressor(CensoredRegressor):
    name = "xgb_aft"

    def __init__(self, params: dict, seed: int = 42):
        self.params = dict(params)
        self.seed = int(seed)
        self.booster = None
        self.feature_names: list[str] | None = None
        self.offset_: float | None = None

    @staticmethod
    def _import_xgboost():
        try:
            import xgboost as xgb
        except ImportError as exc:
            raise ImportError(
                "xgboost is required for model 'xgb_aft'; install project dependencies"
            ) from exc
        return xgb

    @staticmethod
    def _training_offset(labels: LabelIntervals) -> float:
        positive = np.concatenate([labels.lower[labels.lower > 0], labels.upper[labels.upper > 0]])
        if len(positive) == 0:
            return 1e-6
        return max(float(np.nanpercentile(positive, 1)) / 10.0, 1e-8)

    def _matrix(self, X: pd.DataFrame, labels: LabelIntervals | None = None):
        xgb = self._import_xgboost()
        if self.feature_names is not None and list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted XGBoost model")
        matrix = xgb.DMatrix(X, feature_names=list(X.columns), missing=np.nan)
        if labels is not None:
            if self.offset_ is None:
                raise RuntimeError("offset is not initialized")
            lower = np.maximum(labels.lower + self.offset_, self.offset_)
            upper = np.maximum(labels.upper + self.offset_, self.offset_)
            matrix.set_float_info("label_lower_bound", lower.astype(np.float32))
            matrix.set_float_info("label_upper_bound", upper.astype(np.float32))
        return matrix

    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> XGBoostAFTRegressor:
        xgb = self._import_xgboost()
        self.feature_names = list(X.columns)
        self.offset_ = self._training_offset(labels)
        dtrain = self._matrix(X, labels)
        if sample_weight is not None:
            dtrain.set_weight(np.asarray(sample_weight, dtype=np.float32))
        evals = [(dtrain, "train")]
        if X_validation is not None and validation_labels is not None and len(X_validation):
            dvalidation = self._matrix(X_validation, validation_labels)
            evals.append((dvalidation, "validation"))

        params = {
            "objective": "survival:aft",
            "eval_metric": "aft-nloglik",
            "aft_loss_distribution": self.params.get("distribution", "normal"),
            "aft_loss_distribution_scale": float(self.params.get("distribution_scale", 1.0)),
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
        early_stopping = None
        if len(evals) > 1:
            early_stopping = int(self.params.get("early_stopping_rounds", 80))
        self.booster = xgb.train(
            params,
            dtrain,
            num_boost_round=int(self.params.get("num_boost_round", 1200)),
            evals=evals,
            early_stopping_rounds=early_stopping,
            verbose_eval=False,
        )
        return self

    def _latent_quantile_multiplier(self, probability: float) -> float:
        distribution = self.params.get("distribution", "normal")
        scale = float(self.params.get("distribution_scale", 1.0))
        if distribution == "normal":
            latent = ndtri(probability)
        elif distribution == "logistic":
            latent = math.log(probability / (1.0 - probability))
        else:
            # XGBoost's extreme-value parameterization is not exposed as a calibrated
            # quantile API. A normal approximation is deliberately explicit here.
            latent = ndtri(probability)
        return float(math.exp(scale * latent))

    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        if self.booster is None or self.offset_ is None:
            raise RuntimeError("model is not fitted")
        raw_median = np.asarray(self.booster.predict(self._matrix(X)), dtype=float)
        q10 = np.maximum(raw_median * self._latent_quantile_multiplier(0.1) - self.offset_, 0)
        q50 = np.maximum(raw_median - self.offset_, 0)
        q90 = np.maximum(raw_median * self._latent_quantile_multiplier(0.9) - self.offset_, 0)
        return DistributionPrediction(
            q10=q10,
            q50=q50,
            q90=q90,
            extra={
                "distribution": self.params.get("distribution", "normal"),
                "distribution_scale": float(self.params.get("distribution_scale", 1.0)),
                "offset_ug_l": self.offset_,
            },
        )

    def exceedance_probability(self, X: pd.DataFrame, threshold: float) -> np.ndarray:
        if self.booster is None or self.offset_ is None:
            raise RuntimeError("model is not fitted")
        raw_median = np.maximum(np.asarray(self.booster.predict(self._matrix(X)), dtype=float), 1e-12)
        standardized = np.log((float(threshold) + self.offset_) / raw_median) / float(
            self.params.get("distribution_scale", 1.0)
        )
        distribution = self.params.get("distribution", "normal")
        cdf = ndtr(standardized) if distribution == "normal" else expit(standardized)
        return np.clip(1.0 - cdf, 0, 1)
