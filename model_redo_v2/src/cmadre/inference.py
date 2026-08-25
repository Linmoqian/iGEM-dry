"""Reload a completed run and produce calibrated predictions without refitting."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .calibration import CQRCalibrator
from .ensemble import NonNegativeStacker
from .models.base import CensoredRegressor
from .models.tabicl_challenger import TabICLChallenger
from .models.tabm_censored import TabMCensoredRegressor
from .ood import FeatureOODDetector
from .pipeline import _model_artifact_path


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, low_memory=False)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError("prediction input must be CSV or Parquet")


def _write_table(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        frame.to_csv(path, index=False)
    elif path.suffix.lower() in {".parquet", ".pq"}:
        frame.to_parquet(path, index=False)
    else:
        raise ValueError("prediction output must be CSV or Parquet")


def _load_model(run_dir: Path, name: str):
    artifact = _model_artifact_path(run_dir / "models", name)
    if name == "tabm_censored":
        return TabMCensoredRegressor.load(artifact)
    if name == "tabicl":
        return TabICLChallenger.load(artifact)
    return CensoredRegressor.load(artifact)


def predict_from_run(run_dir: str | Path, input_path: str | Path, output_path: str | Path) -> Path:
    run_dir = Path(run_dir).expanduser().resolve()
    status = json.loads((run_dir / "run_status.json").read_text(encoding="utf-8"))
    if status.get("status") != "complete":
        raise ValueError(f"run is not complete: {status.get('status')!r}")
    stacker = NonNegativeStacker.load(run_dir / "stacking_weights.json")
    calibrator = CQRCalibrator.load(run_dir / "calibrator.json")
    ood_detector = FeatureOODDetector.load(run_dir / "ood_detector.pkl")
    models = {name: _load_model(run_dir, name) for name in stacker.model_names}

    raw = _read_table(Path(input_path).expanduser().resolve())
    first = models[stacker.model_names[0]]
    feature_names = getattr(first, "feature_names", None)
    if not feature_names:
        raise ValueError("model artifact does not declare feature names")
    missing_columns = [name for name in feature_names if name not in raw.columns]
    if missing_columns:
        raise ValueError(f"input is missing required feature columns: {missing_columns}")
    features = raw.loc[:, feature_names].apply(pd.to_numeric, errors="coerce")
    base = {name: model.predict_distribution(features) for name, model in models.items()}
    ensemble = stacker.predict(base)
    calibrated = calibrator.transform(ensemble)
    ood = ood_detector.predict(features)

    result = raw.reset_index(drop=True).copy()
    for name, prediction in base.items():
        result = pd.concat([result, prediction.to_frame(prefix=f"{name}__")], axis=1)
    result = pd.concat([result, ensemble.to_frame(prefix="ensemble__")], axis=1)
    result = pd.concat([result, calibrated.to_frame(prefix="calibrated__")], axis=1)
    result["ood_score"] = ood.score
    result["ood_flag"] = ood.flag
    output = Path(output_path).expanduser().resolve()
    _write_table(result, output)
    return output
