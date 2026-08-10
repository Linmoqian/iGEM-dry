"""Point, interval, calibration, risk, and worst-source metrics."""

from __future__ import annotations

from itertools import pairwise
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .labels import LabelIntervals
from .models.base import DistributionPrediction


def _finite_or_none(value: float) -> float | None:
    return float(value) if np.isfinite(value) else None


def _ece(probability: np.ndarray, target: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    result = 0.0
    for left, right in pairwise(edges):
        selected = (probability >= left) & (probability < right if right < 1 else probability <= right)
        if selected.any():
            result += selected.mean() * abs(probability[selected].mean() - target[selected].mean())
    return float(result)


def _average_precision(target: np.ndarray, probability: np.ndarray) -> float | None:
    if len(np.unique(target)) < 2:
        return None
    order = np.argsort(-probability, kind="mergesort")
    y = target[order].astype(float)
    cumulative_true = np.cumsum(y)
    precision = cumulative_true / (np.arange(len(y)) + 1)
    return float((precision * y).sum() / max(y.sum(), 1.0))


def _point_metrics(prediction: np.ndarray, labels: LabelIntervals) -> dict[str, Any]:
    exact = labels.exact & np.isfinite(labels.lower) & np.isfinite(prediction)
    result: dict[str, Any] = {"exact_rows": int(exact.sum())}
    if exact.sum() < 2:
        return result
    y = labels.lower[exact]
    p = prediction[exact]
    errors = p - y
    log_errors = np.log1p(p) - np.log1p(y)
    denominator = np.square(y - y.mean()).sum()
    r2 = np.nan if denominator <= 0 else 1.0 - np.square(errors).sum() / denominator
    spearman = spearmanr(y, p, nan_policy="omit").statistic
    positive = (y > 0) & (p > 0)
    factor2 = np.nan
    if positive.any():
        ratio = np.maximum(p[positive] / y[positive], y[positive] / p[positive])
        factor2 = (ratio <= 2).mean()
    result.update(
        {
            "mae_ug_l": float(np.abs(errors).mean()),
            "median_ae_ug_l": float(np.median(np.abs(errors))),
            "rmse_ug_l": float(np.sqrt(np.square(errors).mean())),
            "log1p_mae": float(np.abs(log_errors).mean()),
            "log1p_rmse": float(np.sqrt(np.square(log_errors).mean())),
            "r2": _finite_or_none(r2),
            "spearman": _finite_or_none(spearman),
            "within_factor_2": _finite_or_none(factor2),
        }
    )
    return result


def evaluate_predictions(
    prediction: DistributionPrediction,
    labels: LabelIntervals,
    metadata: pd.DataFrame | None = None,
    thresholds: list[float] | None = None,
) -> dict[str, Any]:
    point = prediction.q50
    below = np.maximum(labels.lower - point, 0)
    above = np.maximum(point - labels.upper, 0)
    interval_distance = below + above
    compatible = (prediction.q90 >= labels.lower) & (prediction.q10 <= labels.upper)
    exact = labels.exact
    exact_coverage = (
        np.nan
        if exact.sum() == 0
        else (
            (prediction.q10[exact] <= labels.lower[exact]) & (labels.lower[exact] <= prediction.q90[exact])
        ).mean()
    )
    exact_width = np.nan if exact.sum() == 0 else (prediction.q90[exact] - prediction.q10[exact]).mean()
    result: dict[str, Any] = {
        "rows": len(point),
        "exact_rows": int(exact.sum()),
        "censored_rows": int((~exact).sum()),
        "point": _point_metrics(point, labels),
        "interval_distance_mae_ug_l": float(interval_distance.mean()),
        "observation_interval_compatibility": float(compatible.mean()),
        "exact_q10_q90_coverage": _finite_or_none(exact_coverage),
        "exact_q10_q90_mean_width_ug_l": _finite_or_none(exact_width),
    }

    if metadata is not None and "source_group" in metadata:
        source_rows = []
        for source, positions in metadata.groupby("source_group").indices.items():
            index = np.asarray(positions, dtype=int)
            source_label = labels.subset(index)
            source_metric = _point_metrics(point[index], source_label)
            source_rows.append(
                {
                    "source": str(source),
                    "rows": len(index),
                    "exact_rows": source_metric.get("exact_rows", 0),
                    "log1p_mae": source_metric.get("log1p_mae"),
                    "interval_distance_mae_ug_l": float(interval_distance[index].mean()),
                }
            )
        eligible = [row for row in source_rows if row.get("log1p_mae") is not None]
        result["by_source"] = source_rows
        result["source_macro_log1p_mae"] = (
            None if not eligible else float(np.mean([row["log1p_mae"] for row in eligible]))
        )
        result["worst_source_log1p_mae"] = (
            None if not eligible else float(max(row["log1p_mae"] for row in eligible))
        )

    risk_results = {}
    for threshold in thresholds or []:
        known_positive = labels.lower > threshold
        known_negative = labels.upper <= threshold
        known = known_positive | known_negative
        if known.sum() == 0:
            continue
        target = known_positive[known].astype(int)
        probability = prediction.exceedance_probability(threshold)[known]
        risk_results[str(threshold)] = {
            "known_rows": int(known.sum()),
            "ambiguous_rows": int((~known).sum()),
            "positive_rows": int(target.sum()),
            "brier": float(np.square(probability - target).mean()),
            "ece": _ece(probability, target),
            "average_precision": _average_precision(target, probability),
        }
    result["risk_thresholds"] = risk_results
    return result
