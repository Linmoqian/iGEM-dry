"""End-to-end leakage-safe training, stacking, calibration, and evaluation."""

from __future__ import annotations

import importlib.metadata
import json
import logging
import platform
import subprocess
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .calibration import CQRCalibrator
from .config import save_config
from .data import DatasetView, dataset_summary, load_dataset
from .ensemble import NonNegativeStacker
from .metrics import evaluate_predictions
from .models import create_model
from .models.base import DistributionPrediction
from .ood import FeatureOODDetector, OODResult
from .splits import (
    inner_group_folds,
    make_split_manifest,
    split_indices,
    split_summary,
    write_split_artifacts,
)

LOGGER = logging.getLogger("cmadre")


def _now_utc() -> str:
    return datetime.now(UTC).isoformat()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[2],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.SubprocessError, OSError):
        return None


def _package_versions() -> dict[str, str | None]:
    names = [
        "numpy",
        "pandas",
        "scipy",
        "scikit-learn",
        "pyarrow",
        "xgboost",
        "lightgbm",
        "catboost",
        "torch",
        "tabicl",
    ]
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def _json_write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def _run_directory(config: dict, run_name: str | None = None) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    stem = run_name or f"{config['target']}_{config['panel']}_{config['split_protocol']}_{timestamp}"
    safe = "".join(character if character.isalnum() or character in "-_" else "_" for character in stem)
    directory = Path(config["runs_dir"]) / safe
    suffix = 1
    candidate = directory
    while candidate.exists():
        candidate = directory.with_name(f"{directory.name}_{suffix:02d}")
        suffix += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def source_balanced_weights(metadata: pd.DataFrame) -> np.ndarray:
    source = metadata["source_group"].fillna("unknown_source").astype(str)
    counts = source.value_counts()
    weights = source.map(lambda value: 1.0 / counts[value]).to_numpy(dtype=float, copy=True)
    weights /= weights.mean()
    # Avoid an extremely tiny source creating a numerically dominant record.
    weights = np.clip(weights, 0.1, 10.0)
    return weights / weights.mean()


def _empty_prediction(size: int) -> DistributionPrediction:
    values = np.full(size, np.nan, dtype=float)
    return DistributionPrediction(q10=values.copy(), q50=values.copy(), q90=values.copy())


def _generate_oof_predictions(
    data: DatasetView,
    train_indices: np.ndarray,
    model_names: list[str],
    config: dict,
) -> dict[str, DistributionPrediction]:
    train_data = data.subset(train_indices)
    folds = inner_group_folds(
        train_data.metadata,
        n_folds=int(config["stacking_folds"]),
        seed=int(config["seed"]) + 1000,
        outer_protocol=str(config["split_protocol"]),
    )
    fold_ids = sorted(np.unique(folds).tolist())
    storage = {
        name: {
            "q10": np.full(len(train_data.X), np.nan),
            "q50": np.full(len(train_data.X), np.nan),
            "q90": np.full(len(train_data.X), np.nan),
            "p_detected": np.full(len(train_data.X), np.nan),
            "has_probability": False,
        }
        for name in model_names
    }
    for fold_number, fold in enumerate(fold_ids):
        held = np.flatnonzero(folds == fold)
        fitted = np.flatnonzero(folds != fold)
        if len(held) == 0 or len(fitted) == 0:
            raise ValueError(f"empty inner stacking fold {fold}")
        fit_data = train_data.subset(fitted)
        held_data = train_data.subset(held)
        weights = source_balanced_weights(fit_data.metadata)
        for model_number, name in enumerate(model_names):
            LOGGER.info("OOF fold %d/%d: fitting %s", fold_number + 1, len(fold_ids), name)
            model = create_model(name, config, seed_offset=10_000 + fold * 100 + model_number)
            model.fit(
                fit_data.X,
                fit_data.labels,
                X_validation=held_data.X,
                validation_labels=held_data.labels,
                sample_weight=weights,
            )
            prediction = model.predict_distribution(held_data.X)
            storage[name]["q10"][held] = prediction.q10
            storage[name]["q50"][held] = prediction.q50
            storage[name]["q90"][held] = prediction.q90
            if prediction.p_detected is not None:
                storage[name]["p_detected"][held] = prediction.p_detected
                storage[name]["has_probability"] = True
    result = {}
    for name, values in storage.items():
        if not np.isfinite(values["q50"]).all():
            raise ValueError(f"OOF predictions for {name} are incomplete")
        probability = values["p_detected"] if values["has_probability"] else None
        result[name] = DistributionPrediction(
            q10=values["q10"], q50=values["q50"], q90=values["q90"], p_detected=probability
        )
    return result


def _model_artifact_path(models_dir: Path, name: str) -> Path:
    if name == "tabm_censored":
        return models_dir / f"{name}.pt"
    if name == "tabicl":
        return models_dir / name
    return models_dir / f"{name}.pkl"


def _prediction_table(
    data: DatasetView,
    indices: np.ndarray,
    base: dict[str, DistributionPrediction],
    ensemble: DistributionPrediction,
    calibrated: DistributionPrediction,
    ood: OODResult,
) -> pd.DataFrame:
    metadata_columns = [
        "record_id",
        "dataset_id",
        "site_id",
        "waterbody_name",
        "country",
        "sample_date",
        "source_group",
        "waterbody_group",
    ]
    frame = data.metadata.iloc[indices][metadata_columns].reset_index(drop=True).copy()
    labels = data.labels.subset(indices)
    frame["label_lower_ug_l"] = labels.lower
    frame["label_upper_ug_l"] = labels.upper
    frame["label_exact"] = labels.exact
    for name, prediction in base.items():
        frame = pd.concat([frame, prediction.to_frame(prefix=f"{name}__")], axis=1)
    frame = pd.concat([frame, ensemble.to_frame(prefix="ensemble__")], axis=1)
    frame = pd.concat([frame, calibrated.to_frame(prefix="calibrated__")], axis=1)
    frame["ood_score"] = ood.score
    frame["ood_flag"] = ood.flag
    return frame


def run_training(config: dict, run_name: str | None = None) -> Path:
    run_dir = _run_directory(config, run_name)
    models_dir = run_dir / "models"
    models_dir.mkdir()
    status = {
        "status": "running",
        "started_at_utc": _now_utc(),
        "git_commit": _git_commit(),
        "python": sys.version,
        "platform": platform.platform(),
        "hostname": platform.node(),
        "packages": _package_versions(),
    }
    _json_write(run_dir / "run_status.json", status)
    save_config(config, run_dir / "config.json")

    try:
        LOGGER.info("Loading target=%s panel=%s", config["target"], config["panel"])
        data = load_dataset(config)
        _json_write(run_dir / "data_summary.json", dataset_summary(data))
        manifest = make_split_manifest(data, config)
        write_split_artifacts(manifest, run_dir)
        split = split_indices(manifest)
        LOGGER.info(
            "Split rows: train=%d validation=%d test=%d",
            len(split.train),
            len(split.validation),
            len(split.test),
        )

        model_names = list(dict.fromkeys(config["models"]))
        oof_predictions = _generate_oof_predictions(data, split.train, model_names, config)
        train_labels = data.labels.subset(split.train)
        stacker = NonNegativeStacker(
            model_names=model_names,
            censored_weight=float(config.get("censored_stacking_weight", 0.25)),
            fit_transform=str(config.get("stacking_transform", "log1p")),
            objective=str(config.get("stacking_objective", "median_nnls")),
            quantile_loss_weight=float(config.get("stacking_quantile_loss_weight", 0.25)),
            width_penalty=float(config.get("stacking_width_penalty", 0.05)),
            max_log_width=float(config.get("stacking_max_log_width", 4.0)),
            l2_penalty=float(config.get("stacking_l2_penalty", 0.01)),
        ).fit(
            oof_predictions,
            train_labels,
            sample_weight=source_balanced_weights(data.metadata.iloc[split.train]),
        )
        stacker.save(run_dir / "stacking_weights.json")

        train = data.subset(split.train)
        validation = data.subset(split.validation)
        test = data.subset(split.test)
        train_weights = source_balanced_weights(train.metadata)
        ood_detector = FeatureOODDetector(
            threshold_quantile=float(config.get("ood_threshold_quantile", 0.99))
        ).fit(train.X)
        ood_detector.save(run_dir / "ood_detector.pkl")
        validation_ood = ood_detector.predict(validation.X)
        test_ood = ood_detector.predict(test.X)
        validation_predictions: dict[str, DistributionPrediction] = {}
        test_predictions: dict[str, DistributionPrediction] = {}
        for model_number, name in enumerate(model_names):
            LOGGER.info("Fitting final base model: %s", name)
            model = create_model(name, config, seed_offset=model_number)
            model.fit(
                train.X,
                train.labels,
                X_validation=validation.X,
                validation_labels=validation.labels,
                sample_weight=train_weights,
            )
            model.save(_model_artifact_path(models_dir, name))
            validation_predictions[name] = model.predict_distribution(validation.X)
            test_predictions[name] = model.predict_distribution(test.X)

        validation_ensemble = stacker.predict(validation_predictions)
        test_ensemble = stacker.predict(test_predictions)
        calibrator = CQRCalibrator(alpha=float(config["conformal_alpha"])).fit(
            validation_ensemble, validation.labels
        )
        calibrator.save(run_dir / "calibrator.json")
        validation_calibrated = calibrator.transform(validation_ensemble)
        test_calibrated = calibrator.transform(test_ensemble)

        thresholds = [float(value) for value in config.get("risk_thresholds_ug_l", [])]
        metrics = {
            "ood": {
                "method": "training-only Ledoit-Wolf Mahalanobis",
                "threshold_quantile": ood_detector.threshold_quantile,
                "threshold": ood_detector.threshold_,
                "validation_flag_rate": float(validation_ood.flag.mean()),
                "test_flag_rate": float(test_ood.flag.mean()),
            },
            "validation": {
                "base_models": {
                    name: evaluate_predictions(prediction, validation.labels, validation.metadata, thresholds)
                    for name, prediction in validation_predictions.items()
                },
                "ensemble_uncalibrated": evaluate_predictions(
                    validation_ensemble, validation.labels, validation.metadata, thresholds
                ),
                "ensemble_calibrated": evaluate_predictions(
                    validation_calibrated, validation.labels, validation.metadata, thresholds
                ),
            },
            "test": {
                "base_models": {
                    name: evaluate_predictions(prediction, test.labels, test.metadata, thresholds)
                    for name, prediction in test_predictions.items()
                },
                "ensemble_uncalibrated": evaluate_predictions(
                    test_ensemble, test.labels, test.metadata, thresholds
                ),
                "ensemble_calibrated": evaluate_predictions(
                    test_calibrated, test.labels, test.metadata, thresholds
                ),
            },
        }
        _json_write(run_dir / "metrics.json", metrics)
        _prediction_table(
            data,
            split.validation,
            validation_predictions,
            validation_ensemble,
            validation_calibrated,
            validation_ood,
        ).to_parquet(run_dir / "validation_predictions.parquet", index=False)
        _prediction_table(
            data, split.test, test_predictions, test_ensemble, test_calibrated, test_ood
        ).to_parquet(run_dir / "test_predictions.parquet", index=False)

        status.update(
            {
                "status": "complete",
                "completed_at_utc": _now_utc(),
                "models": model_names,
                "split_summary": split_summary(manifest),
                "data_sha256": data.source_sha256,
            }
        )
        _json_write(run_dir / "run_status.json", status)
        LOGGER.info("Run complete: %s", run_dir)
        return run_dir
    except Exception as exc:
        status.update(
            {
                "status": "failed",
                "failed_at_utc": _now_utc(),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
        _json_write(run_dir / "run_status.json", status)
        raise
