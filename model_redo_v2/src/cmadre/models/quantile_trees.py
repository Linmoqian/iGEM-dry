"""Strong quantile tree challengers with explicit censored-label approximation."""

from __future__ import annotations

import inspect

import numpy as np
import pandas as pd

from ..labels import LabelIntervals, interval_midpoint
from .base import CensoredRegressor, DistributionPrediction

QUANTILES = (0.1, 0.5, 0.9)


def _proxy_target_and_weights(
    labels: LabelIntervals, censored_weight: float, sample_weight: np.ndarray | None
) -> tuple[np.ndarray, np.ndarray]:
    target = np.log1p(interval_midpoint(labels))
    weights = np.where(labels.exact, 1.0, float(censored_weight))
    if sample_weight is not None:
        weights = weights * np.asarray(sample_weight, dtype=float)
    return target, weights


class CatBoostQuantileRegressor(CensoredRegressor):
    """Three CatBoost quantile models.

    This model does not implement interval likelihood. Censored labels are represented
    by interval midpoints and downweighted, so it is a challenger rather than the
    censor-aware statistical core.
    """

    name = "catboost_quantile"

    def __init__(self, params: dict, seed: int = 42):
        self.params = dict(params)
        self.seed = int(seed)
        self.models: dict[float, object] = {}
        self.feature_names: list[str] | None = None

    @staticmethod
    def _model_class():
        try:
            from catboost import CatBoostRegressor
        except ImportError as exc:
            raise ImportError("catboost is required for model 'catboost_quantile'") from exc
        return CatBoostRegressor

    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> CatBoostQuantileRegressor:
        CatBoostRegressor = self._model_class()
        self.feature_names = list(X.columns)
        y, weights = _proxy_target_and_weights(
            labels, float(self.params.get("censored_weight", 0.25)), sample_weight
        )
        eval_set = None
        if X_validation is not None and validation_labels is not None and len(X_validation):
            y_validation = np.log1p(interval_midpoint(validation_labels))
            eval_set = (X_validation, y_validation)
        for quantile in QUANTILES:
            model_kwargs = {
                "loss_function": f"Quantile:alpha={quantile}",
                "eval_metric": f"Quantile:alpha={quantile}",
                "iterations": int(self.params.get("iterations", 1200)),
                "depth": int(self.params.get("depth", 7)),
                "learning_rate": float(self.params.get("learning_rate", 0.035)),
                "l2_leaf_reg": float(self.params.get("l2_leaf_reg", 5.0)),
                "random_seed": self.seed,
                "task_type": self.params.get("task_type", "CPU"),
                "thread_count": int(self.params.get("thread_count", -1)),
                "allow_writing_files": False,
                "verbose": False,
            }
            if str(model_kwargs["task_type"]).upper() == "GPU":
                model_kwargs["devices"] = str(self.params.get("devices", "0"))
                model_kwargs["gpu_ram_part"] = float(self.params.get("gpu_ram_part", 0.75))
            model = CatBoostRegressor(
                **model_kwargs,
            )
            fit_kwargs = {"sample_weight": weights, "verbose": False}
            if eval_set is not None:
                fit_kwargs.update(
                    {
                        "eval_set": eval_set,
                        "early_stopping_rounds": int(self.params.get("early_stopping_rounds", 80)),
                        "use_best_model": True,
                    }
                )
            model.fit(X, y, **fit_kwargs)
            self.models[quantile] = model
        return self

    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        if set(self.models) != set(QUANTILES):
            raise RuntimeError("model is not fitted")
        if list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted CatBoost model")
        predictions = [np.maximum(np.expm1(self.models[q].predict(X)), 0) for q in QUANTILES]
        return DistributionPrediction(q10=predictions[0], q50=predictions[1], q90=predictions[2])


class LightGBMQuantileRegressor(CensoredRegressor):
    """Three LightGBM quantile models with the same transparent ND approximation."""

    name = "lightgbm_quantile"

    def __init__(self, params: dict, seed: int = 42):
        self.params = dict(params)
        self.seed = int(seed)
        self.models: dict[float, object] = {}
        self.feature_names: list[str] | None = None

    @staticmethod
    def _imports():
        try:
            import lightgbm as lgb
            from lightgbm import LGBMRegressor
        except ImportError as exc:
            raise ImportError("lightgbm is required for model 'lightgbm_quantile'") from exc
        return lgb, LGBMRegressor

    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> LightGBMQuantileRegressor:
        lgb, LGBMRegressor = self._imports()
        self.feature_names = list(X.columns)
        y, weights = _proxy_target_and_weights(
            labels, float(self.params.get("censored_weight", 0.25)), sample_weight
        )
        validation_pair = None
        callbacks = None
        if X_validation is not None and validation_labels is not None and len(X_validation):
            validation_pair = (X_validation, np.log1p(interval_midpoint(validation_labels)))
            callbacks = [lgb.early_stopping(int(self.params.get("early_stopping_rounds", 80)), verbose=False)]
        for quantile in QUANTILES:
            model = LGBMRegressor(
                objective="quantile",
                alpha=quantile,
                n_estimators=int(self.params.get("n_estimators", 1500)),
                learning_rate=float(self.params.get("learning_rate", 0.025)),
                num_leaves=int(self.params.get("num_leaves", 31)),
                min_child_samples=int(self.params.get("min_child_samples", 30)),
                subsample=float(self.params.get("subsample", 0.85)),
                colsample_bytree=float(self.params.get("colsample_bytree", 0.85)),
                reg_lambda=float(self.params.get("reg_lambda", 2.0)),
                random_state=self.seed,
                n_jobs=int(self.params.get("n_jobs", -1)),
                verbosity=-1,
            )
            fit_kwargs = {"sample_weight": weights, "callbacks": callbacks}
            if validation_pair is not None:
                # LightGBM 4.7 introduced eval_X/eval_y and deprecated eval_set;
                # retain compatibility with supported earlier 4.x releases.
                if "eval_X" in inspect.signature(model.fit).parameters:
                    fit_kwargs.update({"eval_X": validation_pair[0], "eval_y": validation_pair[1]})
                else:
                    fit_kwargs["eval_set"] = [validation_pair]
            model.fit(X, y, **fit_kwargs)
            self.models[quantile] = model
        return self

    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        if set(self.models) != set(QUANTILES):
            raise RuntimeError("model is not fitted")
        if list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted LightGBM model")
        predictions = [np.maximum(np.expm1(self.models[q].predict(X)), 0) for q in QUANTILES]
        return DistributionPrediction(q10=predictions[0], q50=predictions[1], q90=predictions[2])
