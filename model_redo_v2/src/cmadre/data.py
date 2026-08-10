"""Loading, filtering, fingerprinting, and summarizing model-ready tables."""

from __future__ import annotations

import hashlib
import json
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .features import resolve_features
from .labels import LabelIntervals, build_label_intervals

TABLES = {
    "total_microcystins": {
        "core_field": "total_microcystins_enriched_dynamic_ready.csv",
        "bloom_augmented": "total_microcystins_enriched_dynamic_ready.csv",
        "static_context": "total_microcystins_enriched_static_baseline_ready.csv",
        "hybrid": "total_microcystins_enriched_static_baseline_ready.csv",
    },
    "mc_lr": {
        "core_field": "mc_lr_enriched_dynamic_ready.csv",
        "bloom_augmented": "mc_lr_enriched_dynamic_ready.csv",
        "static_context": "mc_lr_enriched_static_baseline_ready.csv",
        "hybrid": "mc_lr_enriched_static_baseline_ready.csv",
    },
}

METADATA_COLUMNS = [
    "record_id",
    "dataset_id",
    "site_id",
    "waterbody_name",
    "country",
    "state_region",
    "sample_date",
    "year",
    "month",
    "latitude",
    "longitude",
    "method",
    "matrix",
    "target_kind",
    "target_quality_flag",
]


@dataclass
class DatasetView:
    X: pd.DataFrame
    labels: LabelIntervals
    metadata: pd.DataFrame
    feature_names: list[str]
    requested_but_missing_features: list[str]
    source_path: Path
    source_sha256: str
    target: str
    panel: str

    def subset(self, indices: np.ndarray | list[int]) -> DatasetView:
        positions = np.asarray(indices)
        return DatasetView(
            X=self.X.iloc[positions].reset_index(drop=True),
            labels=self.labels.subset(positions),
            metadata=self.metadata.iloc[positions].reset_index(drop=True),
            feature_names=list(self.feature_names),
            requested_but_missing_features=list(self.requested_but_missing_features),
            source_path=self.source_path,
            source_sha256=self.source_sha256,
            target=self.target,
            panel=self.panel,
        )


def sha256_file(path: str | Path, block_size: int = 2**20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(block_size):
            digest.update(chunk)
    return digest.hexdigest()


def table_path(data_dir: str | Path, target: str, panel: str) -> Path:
    try:
        filename = TABLES[target][panel]
    except KeyError as exc:
        raise ValueError(f"unsupported target/panel combination: {target}/{panel}") from exc
    path = Path(data_dir) / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return path.resolve()


def _waterbody_group(metadata: pd.DataFrame) -> pd.Series:
    waterbody = (
        metadata.get("waterbody_name", pd.Series(index=metadata.index, dtype=object))
        .fillna("")
        .astype(str)
        .str.strip()
    )
    site = (
        metadata.get("site_id", pd.Series(index=metadata.index, dtype=object))
        .fillna("")
        .astype(str)
        .str.strip()
    )
    source = (
        metadata.get("dataset_id", pd.Series(index=metadata.index, dtype=object))
        .fillna("unknown")
        .astype(str)
    )
    record = metadata["record_id"].astype(str)
    key = np.where(waterbody.ne(""), "waterbody:" + source + ":" + waterbody, "")
    key = np.where((key == "") & site.ne(""), "site:" + source + ":" + site, key)
    key = np.where(key == "", "record:" + record, key)
    return pd.Series(key, index=metadata.index, dtype="string")


def load_dataset(config: dict) -> DatasetView:
    path = table_path(config["data_dir"], config["target"], config["panel"])
    frame = pd.read_csv(path, low_memory=False)
    if "record_id" not in frame:
        raise ValueError(f"{path.name} does not contain record_id")
    if frame["record_id"].isna().any() or frame["record_id"].duplicated().any():
        raise ValueError(f"{path.name} must have unique, non-null record_id values")

    labels = build_label_intervals(frame)
    features, absent = resolve_features(config["panel"], frame.columns)
    X = frame[features].apply(pd.to_numeric, errors="coerce")
    all_missing = [column for column in X if X[column].notna().sum() == 0]
    if all_missing:
        warnings.warn(f"dropping all-missing features: {all_missing}", stacklevel=2)
        X = X.drop(columns=all_missing)
        features = [column for column in features if column not in all_missing]
    if not features:
        raise ValueError("all selected features are missing")

    minimum_feature_count = int(config.get("minimum_feature_count", 1))
    feature_ok = X.notna().sum(axis=1).to_numpy() >= minimum_feature_count
    source = frame.get("dataset_id", pd.Series("unknown_source", index=frame.index)).fillna(
        "unknown_source"
    ).astype(str)
    source_ok = np.ones(len(frame), dtype=bool)
    include_sources = {str(value) for value in config.get("include_sources", [])}
    exclude_sources = {str(value) for value in config.get("exclude_sources", [])}
    if include_sources & exclude_sources:
        raise ValueError("include_sources and exclude_sources must not overlap")
    if include_sources:
        source_ok &= source.isin(include_sources).to_numpy()
    if exclude_sources:
        source_ok &= ~source.isin(exclude_sources).to_numpy()
    valid = labels.valid & feature_ok & source_ok
    if not valid.any():
        raise ValueError("no records remain after label and feature validation")

    metadata = pd.DataFrame(index=frame.index)
    for column in METADATA_COLUMNS:
        metadata[column] = frame.get(column, np.nan)
    metadata["source_group"] = metadata["dataset_id"].fillna("unknown_source").astype(str)
    metadata["waterbody_group"] = _waterbody_group(metadata)
    metadata["sample_datetime"] = pd.to_datetime(metadata["sample_date"], errors="coerce")
    metadata["label_exclusion_reason"] = labels.exclusion_reason
    metadata["label_limit_source"] = labels.limit_source

    positions = np.flatnonzero(valid)
    result = DatasetView(
        X=X.iloc[positions].reset_index(drop=True).astype(np.float32),
        labels=labels.subset(positions),
        metadata=metadata.iloc[positions].reset_index(drop=True),
        feature_names=list(X.columns),
        requested_but_missing_features=[*absent, *all_missing],
        source_path=path,
        source_sha256=sha256_file(path),
        target=config["target"],
        panel=config["panel"],
    )
    if result.labels.exact.sum() == len(result.labels.exact):
        warnings.warn(
            f"{path.name} contains no usable censored records after filtering; censor-aware models reduce to exact regression",
            stacklevel=2,
        )
    return result


def dataset_summary(data: DatasetView) -> dict:
    dates = data.metadata["sample_datetime"]
    return {
        "source_file": str(data.source_path),
        "source_sha256": data.source_sha256,
        "target": data.target,
        "panel": data.panel,
        "rows": len(data.X),
        "features": len(data.feature_names),
        "feature_names": data.feature_names,
        "requested_but_missing_features": data.requested_but_missing_features,
        "exact_rows": int(data.labels.exact.sum()),
        "censored_rows": int((~data.labels.exact).sum()),
        "source_groups": int(data.metadata["source_group"].nunique()),
        "waterbody_groups": int(data.metadata["waterbody_group"].nunique()),
        "dated_rows": int(dates.notna().sum()),
        "date_min": None if dates.notna().sum() == 0 else dates.min().date().isoformat(),
        "date_max": None if dates.notna().sum() == 0 else dates.max().date().isoformat(),
        "feature_non_null_fraction": {
            column: float(data.X[column].notna().mean()) for column in data.feature_names
        },
    }


def write_dataset_summary(data: DatasetView, path: str | Path) -> None:
    Path(path).write_text(json.dumps(dataset_summary(data), ensure_ascii=False, indent=2), encoding="utf-8")
