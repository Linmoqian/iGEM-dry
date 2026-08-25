"""Construction and validation of exact and censored concentration intervals."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

_LESS_THAN_NUMBER = re.compile(r"<\s*([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)")


@dataclass(frozen=True)
class LabelIntervals:
    lower: np.ndarray
    upper: np.ndarray
    exact: np.ndarray
    detected: np.ndarray
    valid: np.ndarray
    exclusion_reason: np.ndarray
    limit_source: np.ndarray

    def subset(self, mask: np.ndarray) -> LabelIntervals:
        return LabelIntervals(
            lower=self.lower[mask],
            upper=self.upper[mask],
            exact=self.exact[mask],
            detected=self.detected[mask],
            valid=self.valid[mask],
            exclusion_reason=self.exclusion_reason[mask],
            limit_source=self.limit_source[mask],
        )


def _numeric(frame: pd.DataFrame, column: str) -> np.ndarray:
    if column not in frame:
        return np.full(len(frame), np.nan, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=float)


def _boolean(frame: pd.DataFrame, column: str, default: bool = False) -> np.ndarray:
    if column not in frame:
        return np.full(len(frame), default, dtype=bool)
    values = frame[column]
    numeric = pd.to_numeric(values, errors="coerce")
    result = numeric.fillna(1 if default else 0).astype(bool).to_numpy()
    return result


def _limit_from_raw(frame: pd.DataFrame) -> np.ndarray:
    raw = frame.get("target_raw", pd.Series([None] * len(frame), index=frame.index))
    values = np.full(len(frame), np.nan, dtype=float)
    for index, item in enumerate(raw):
        match = _LESS_THAN_NUMBER.search(str(item))
        if match:
            values[index] = float(match.group(1))
    return values


def build_label_intervals(frame: pd.DataFrame) -> LabelIntervals:
    """Build [lower, upper] concentration labels without inventing exact ND values."""
    n_rows = len(frame)
    censored = _boolean(frame, "is_censored", default=False)
    observed = _numeric(frame, "target_ug_l")
    model_value = _numeric(frame, "target_model_ug_l")
    exact_value = np.where(np.isfinite(observed), observed, model_value)

    limit_candidates = [
        ("censor_limit_ug_l", _numeric(frame, "censor_limit_ug_l")),
        ("detection_limit_ug_l", _numeric(frame, "detection_limit_ug_l")),
        ("reporting_limit_ug_l", _numeric(frame, "reporting_limit_ug_l")),
        ("target_raw", _limit_from_raw(frame)),
    ]
    censor_limit = np.full(n_rows, np.nan, dtype=float)
    limit_source = np.full(n_rows, "", dtype=object)
    for source, values in limit_candidates:
        take = ~np.isfinite(censor_limit) & np.isfinite(values) & (values >= 0)
        censor_limit[take] = values[take]
        limit_source[take] = source

    lower = np.where(censored, 0.0, exact_value)
    upper = np.where(censored, censor_limit, exact_value)
    exact = ~censored & np.isfinite(exact_value) & (exact_value >= 0)

    detected_raw = _numeric(frame, "detected")
    detected = np.where(np.isfinite(detected_raw), detected_raw > 0, exact).astype(bool)

    reason = np.full(n_rows, "", dtype=object)
    quality = (
        frame.get("target_quality_flag", pd.Series([""] * n_rows, index=frame.index)).fillna("").astype(str)
    )
    negative_flag = quality.str.contains("negative_excluded", case=False, regex=False).to_numpy()
    reason[negative_flag] = "negative_quality_flag"
    reason[(reason == "") & ~censored & (~np.isfinite(exact_value))] = "missing_exact_value"
    reason[(reason == "") & ~censored & np.isfinite(exact_value) & (exact_value < 0)] = "negative_exact_value"
    reason[(reason == "") & censored & (~np.isfinite(censor_limit))] = "censor_limit_missing"
    reason[(reason == "") & censored & np.isfinite(censor_limit) & (censor_limit < 0)] = (
        "negative_censor_limit"
    )
    reason[(reason == "") & np.isfinite(lower) & np.isfinite(upper) & (upper < lower)] = "invalid_interval"
    valid = reason == ""

    if np.any(valid & (~np.isfinite(lower) | ~np.isfinite(upper))):
        raise AssertionError("valid labels must have finite bounds")
    if np.any(valid & (lower < 0)):
        raise AssertionError("valid concentrations must be non-negative")
    if np.any(valid & (upper < lower)):
        raise AssertionError("valid label upper bounds must not be below lower bounds")

    return LabelIntervals(
        lower=lower,
        upper=upper,
        exact=exact,
        detected=detected,
        valid=valid,
        exclusion_reason=reason,
        limit_source=limit_source,
    )


def interval_midpoint(labels: LabelIntervals) -> np.ndarray:
    """Transparent approximation for models that do not support censoring."""
    return np.where(labels.exact, labels.lower, (labels.lower + labels.upper) / 2.0)
