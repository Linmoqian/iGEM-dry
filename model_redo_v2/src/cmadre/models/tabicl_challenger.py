"""Optional TabICLv2 regression challenger.

TabICLv2 has no native interval-censored objective. By default this wrapper fits
only exact observations and returns point predictions; it must not be presented
as the censor-aware core or as a calibrated interval model.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ..labels import LabelIntervals, interval_midpoint
from .base import CensoredRegressor, DistributionPrediction
from .preprocessing import RobustNumericPreprocessor


class TabICLChallenger(CensoredRegressor):
    name = "tabicl"

    def __init__(self, params: dict, seed: int = 42):
        self.params = dict(params)
        self.seed = int(seed)
        self.preprocessor = RobustNumericPreprocessor(add_missing_indicators=True)
        self.model = None
        self.feature_names: list[str] | None = None

    @staticmethod
    def _model_class():
        try:
            from tabicl import TabICLRegressor
        except ImportError as exc:
            raise ImportError("tabicl is optional; install with: pip install -e '.[foundation]'") from exc
        return TabICLRegressor

    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> TabICLChallenger:
        del X_validation, validation_labels, sample_weight
        TabICLRegressor = self._model_class()
        self.feature_names = list(X.columns)
        transformed = self.preprocessor.fit_transform(X)
        exact_only = bool(self.params.get("exact_only", True))
        selected = labels.exact if exact_only else np.ones(len(X), dtype=bool)
        if selected.sum() < 30:
            raise ValueError("TabICL challenger requires at least 30 selected training observations")
        target = labels.lower if exact_only else interval_midpoint(labels)
        self.model = TabICLRegressor(
            n_estimators=int(self.params.get("n_estimators", 8)),
            batch_size=int(self.params.get("batch_size", 8)),
            device=self.params.get("device"),
            random_state=self.seed,
            verbose=bool(self.params.get("verbose", False)),
        )
        self.model.fit(transformed[selected], np.log1p(target[selected]))
        return self

    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        if self.model is None or self.feature_names is None:
            raise RuntimeError("model is not fitted")
        if list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted TabICL model")
        point = np.maximum(np.expm1(self.model.predict(self.preprocessor.transform(X))), 0)
        return DistributionPrediction(q10=point, q50=point, q90=point, extra={"point_only": True})

    def save(self, path: str | Path) -> None:
        if self.model is None:
            raise RuntimeError("model is not fitted")
        import pickle

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.model.save(
            path / "tabicl.pkl", save_model_weights=False, save_training_data=True, save_kv_cache=True
        )
        with (path / "wrapper.pkl").open("wb") as handle:
            pickle.dump(
                {
                    "params": self.params,
                    "seed": self.seed,
                    "feature_names": self.feature_names,
                    "preprocessor": self.preprocessor,
                },
                handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        (path / "artifact.json").write_text(
            json.dumps({"type": self.name, "point_only": True}, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: str | Path) -> TabICLChallenger:
        import pickle

        path = Path(path)
        with (path / "wrapper.pkl").open("rb") as handle:
            wrapper = pickle.load(handle)
        result = cls(wrapper["params"], wrapper["seed"])
        result.feature_names = wrapper["feature_names"]
        result.preprocessor = wrapper["preprocessor"]
        result.model = result._model_class().load(path / "tabicl.pkl", device=result.params.get("device"))
        return result
