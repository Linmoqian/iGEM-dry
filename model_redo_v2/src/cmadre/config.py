"""Configuration loading, validation, and path resolution."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "default.json"


def _deep_update(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_update(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | Path | None = None, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Load defaults, merge a user config, then apply in-memory overrides."""
    config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    if path is not None:
        user_path = Path(path).expanduser().resolve()
        user = json.loads(user_path.read_text(encoding="utf-8"))
        config = _deep_update(config, user)
    if overrides:
        config = _deep_update(config, overrides)

    for key in ("data_dir", "runs_dir"):
        value = Path(config[key]).expanduser()
        if not value.is_absolute():
            value = PROJECT_ROOT / value
        config[key] = str(value.resolve())
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    if config["target"] not in {"total_microcystins", "mc_lr"}:
        raise ValueError("target must be 'total_microcystins' or 'mc_lr'")
    if config["panel"] not in {"core_field", "static_context", "bloom_augmented", "hybrid"}:
        raise ValueError("unknown feature panel")
    if config["split_protocol"] not in {"source_ood", "waterbody_ood", "temporal_ood"}:
        raise ValueError("unknown split protocol")
    n_folds = int(config["n_folds"])
    if n_folds < 3:
        raise ValueError("n_folds must be at least 3")
    test_fold = int(config["test_fold"])
    validation_fold = int(config["validation_fold"])
    if test_fold == validation_fold or not (0 <= test_fold < n_folds) or not (0 <= validation_fold < n_folds):
        raise ValueError("test_fold and validation_fold must be distinct values in [0, n_folds)")
    if not 0 < float(config["conformal_alpha"]) < 1:
        raise ValueError("conformal_alpha must be in (0, 1)")
    if config.get("conformal_transform", "identity") not in {"identity", "log1p"}:
        raise ValueError("conformal_transform must be 'identity' or 'log1p'")
    if not 0.5 < float(config.get("ood_threshold_quantile", 0.99)) < 1:
        raise ValueError("ood_threshold_quantile must be in (0.5, 1)")
    if int(config["stacking_folds"]) < 2:
        raise ValueError("stacking_folds must be at least 2")
    if config.get("stacking_transform", "log1p") not in {"log1p", "identity"}:
        raise ValueError("stacking_transform must be 'log1p' or 'identity'")
    if config.get("stacking_objective", "median_nnls") not in {"median_nnls", "distributional"}:
        raise ValueError("stacking_objective must be 'median_nnls' or 'distributional'")
    if not config.get("models"):
        raise ValueError("at least one model is required")


def save_config(config: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
