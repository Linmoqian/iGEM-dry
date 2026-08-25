"""Fold-safe feature-space out-of-distribution scoring."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

from .models.preprocessing import RobustNumericPreprocessor


@dataclass
class OODResult:
    score: np.ndarray
    flag: np.ndarray


class FeatureOODDetector:
    """Shrinkage-Mahalanobis detector fitted on training features only.

    The shrinkage covariance remains invertible when missingness indicators or
    environmental variables are collinear. Scores are squared Mahalanobis
    distances in the fold-local robust standardized feature space.
    """

    def __init__(self, threshold_quantile: float = 0.99):
        if not 0.5 < float(threshold_quantile) < 1.0:
            raise ValueError("threshold_quantile must be between 0.5 and 1")
        self.threshold_quantile = float(threshold_quantile)
        self.preprocessor = RobustNumericPreprocessor(add_missing_indicators=True)
        self.location_: np.ndarray | None = None
        self.precision_: np.ndarray | None = None
        self.threshold_: float | None = None

    def fit(self, X: pd.DataFrame) -> FeatureOODDetector:
        transformed = self.preprocessor.fit_transform(X).astype(float)
        estimator = LedoitWolf(assume_centered=False).fit(transformed)
        self.location_ = estimator.location_.astype(float, copy=True)
        self.precision_ = estimator.precision_.astype(float, copy=True)
        train_scores = self._score_transformed(transformed)
        self.threshold_ = float(np.quantile(train_scores, self.threshold_quantile, method="higher"))
        return self

    def _score_transformed(self, transformed: np.ndarray) -> np.ndarray:
        if self.location_ is None or self.precision_ is None:
            raise RuntimeError("OOD detector is not fitted")
        centered = transformed - self.location_
        return np.maximum(np.einsum("ij,jk,ik->i", centered, self.precision_, centered), 0.0)

    def predict(self, X: pd.DataFrame) -> OODResult:
        if self.threshold_ is None:
            raise RuntimeError("OOD detector is not fitted")
        score = self._score_transformed(self.preprocessor.transform(X).astype(float))
        return OODResult(score=score, flag=score > self.threshold_)

    def save(self, path: str | Path) -> None:
        if self.threshold_ is None:
            raise RuntimeError("OOD detector is not fitted")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path: str | Path) -> FeatureOODDetector:
        with Path(path).open("rb") as handle:
            detector = pickle.load(handle)
        if not isinstance(detector, cls):
            raise TypeError("artifact is not a FeatureOODDetector")
        return detector
