"""Fold-local numeric preprocessing for neural and foundation models."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class RobustNumericPreprocessor:
    add_missing_indicators: bool = True
    medians_: np.ndarray | None = None
    lower_clip_: np.ndarray | None = None
    upper_clip_: np.ndarray | None = None
    means_: np.ndarray | None = None
    scales_: np.ndarray | None = None
    columns_: list[str] | None = None

    def fit(self, X: pd.DataFrame) -> RobustNumericPreprocessor:
        values = X.to_numpy(dtype=float)
        self.columns_ = list(X.columns)
        finite = np.isfinite(values)
        counts = finite.sum(axis=0)
        # Compute only non-empty columns to avoid NumPy's all-NaN-slice warning in
        # source-held-out folds. A fold-local all-missing feature is represented by
        # zero plus its missingness indicator.
        self.medians_ = np.zeros(values.shape[1], dtype=float)
        populated = counts > 0
        if populated.any():
            self.medians_[populated] = np.nanmedian(values[:, populated], axis=0)
        filled = np.where(np.isfinite(values), values, self.medians_)
        self.lower_clip_ = np.nanpercentile(filled, 0.5, axis=0)
        self.upper_clip_ = np.nanpercentile(filled, 99.5, axis=0)
        clipped = np.clip(filled, self.lower_clip_, self.upper_clip_)
        self.means_ = clipped.mean(axis=0)
        self.scales_ = clipped.std(axis=0)
        self.scales_ = np.where(self.scales_ > 1e-8, self.scales_, 1.0)
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if self.columns_ is None or self.medians_ is None:
            raise RuntimeError("preprocessor is not fitted")
        if list(X.columns) != self.columns_:
            raise ValueError("feature columns/order differ from fitted preprocessor")
        values = X.to_numpy(dtype=float)
        missing = ~np.isfinite(values)
        filled = np.where(missing, self.medians_, values)
        clipped = np.clip(filled, self.lower_clip_, self.upper_clip_)
        standardized = (clipped - self.means_) / self.scales_
        if self.add_missing_indicators:
            standardized = np.concatenate([standardized, missing.astype(float)], axis=1)
        return standardized.astype(np.float32)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        return self.fit(X).transform(X)
