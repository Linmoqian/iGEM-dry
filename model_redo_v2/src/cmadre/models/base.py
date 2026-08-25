"""Shared model protocol and distribution prediction container."""

from __future__ import annotations

import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..labels import LabelIntervals


@dataclass
class DistributionPrediction:
    q10: np.ndarray
    q50: np.ndarray
    q90: np.ndarray
    p_detected: np.ndarray | None = None
    extra: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        arrays = [
            np.asarray(self.q10, dtype=float),
            np.asarray(self.q50, dtype=float),
            np.asarray(self.q90, dtype=float),
        ]
        if not (len(arrays[0]) == len(arrays[1]) == len(arrays[2])):
            raise ValueError("quantile predictions have inconsistent lengths")
        stacked = np.sort(np.vstack(arrays), axis=0)
        self.q10 = np.clip(stacked[0], 0, None)
        self.q50 = np.clip(stacked[1], 0, None)
        self.q90 = np.clip(stacked[2], 0, None)
        if self.p_detected is not None:
            self.p_detected = np.clip(np.asarray(self.p_detected, dtype=float), 0, 1)

    def to_frame(self, prefix: str = "") -> pd.DataFrame:
        frame = pd.DataFrame(
            {
                f"{prefix}q10_ug_l": self.q10,
                f"{prefix}median_ug_l": self.q50,
                f"{prefix}q90_ug_l": self.q90,
            }
        )
        if self.p_detected is not None:
            frame[f"{prefix}p_detected"] = self.p_detected
        return frame

    def exceedance_probability(self, threshold: float) -> np.ndarray:
        """Piecewise-linear CDF approximation from q10/q50/q90."""
        t = float(threshold)
        result = np.empty(len(self.q50), dtype=float)
        low = t <= self.q10
        middle_low = (t > self.q10) & (t <= self.q50)
        middle_high = (t > self.q50) & (t <= self.q90)
        high = t > self.q90
        result[low] = 0.9 + 0.1 * np.clip((self.q10[low] - t) / np.maximum(self.q10[low], 1e-12), 0, 1)
        result[middle_low] = 0.9 - 0.4 * (t - self.q10[middle_low]) / np.maximum(
            self.q50[middle_low] - self.q10[middle_low], 1e-12
        )
        result[middle_high] = 0.5 - 0.4 * (t - self.q50[middle_high]) / np.maximum(
            self.q90[middle_high] - self.q50[middle_high], 1e-12
        )
        result[high] = 0.1 * np.exp(-(t - self.q90[high]) / np.maximum(self.q90[high] + 1e-6, 1e-6))
        return np.clip(result, 0, 1)


class CensoredRegressor(ABC):
    name = "abstract"

    @abstractmethod
    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> CensoredRegressor:
        raise NotImplementedError

    @abstractmethod
    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        raise NotImplementedError

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path: str | Path) -> CensoredRegressor:
        with Path(path).open("rb") as handle:
            model = pickle.load(handle)
        if not isinstance(model, CensoredRegressor):
            raise TypeError("artifact is not a CensoredRegressor")
        return model
