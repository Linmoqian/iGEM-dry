"""Deterministic source-, waterbody-, and time-aware split construction."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .data import DatasetView


@dataclass(frozen=True)
class SplitIndices:
    train: np.ndarray
    validation: np.ndarray
    test: np.ndarray


def _stable_tie_key(value: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}:{value}".encode()).hexdigest()


def balanced_group_folds(groups: pd.Series, n_folds: int, seed: int) -> np.ndarray:
    """Assign whole groups to approximately size-balanced deterministic folds."""
    normalized = groups.fillna("<missing>").astype(str)
    counts = normalized.value_counts().to_dict()
    if len(counts) < n_folds:
        raise ValueError(f"need at least {n_folds} unique groups, found {len(counts)}")
    ordered = sorted(counts, key=lambda key: (-counts[key], _stable_tie_key(key, seed)))
    fold_sizes = np.zeros(n_folds, dtype=np.int64)
    assignment: dict[str, int] = {}
    for group in ordered:
        minimum = fold_sizes.min()
        candidate_folds = np.flatnonzero(fold_sizes == minimum)
        fold = int(candidate_folds[int(_stable_tie_key(group, seed + 1), 16) % len(candidate_folds)])
        assignment[group] = fold
        fold_sizes[fold] += counts[group]
    return normalized.map(assignment).to_numpy(dtype=np.int16)


def temporal_folds(metadata: pd.DataFrame, n_folds: int) -> np.ndarray:
    """Assign fold 0 to the newest block and larger fold IDs to older data."""
    result = np.full(len(metadata), n_folds - 1, dtype=np.int16)
    sources = metadata["source_group"].fillna("unknown_source").astype(str)
    dates = pd.to_datetime(metadata["sample_datetime"], errors="coerce")
    for source in sources.unique():
        index = np.flatnonzero((sources == source).to_numpy() & dates.notna().to_numpy())
        if len(index) == 0:
            continue
        source_dates = dates.iloc[index]
        unique_dates = np.array(sorted(source_dates.dt.normalize().unique()))
        if len(unique_dates) == 1:
            result[index] = n_folds - 1
            continue
        date_blocks = np.array_split(unique_dates, min(n_folds, len(unique_dates)))
        mapping: dict[pd.Timestamp, int] = {}
        # array_split is oldest -> newest; reverse IDs so fold 0 is always newest.
        for chronological_block, values in enumerate(date_blocks):
            fold = len(date_blocks) - chronological_block - 1
            for value in values:
                mapping[pd.Timestamp(value)] = fold
        assigned = source_dates.dt.normalize().map(mapping).fillna(n_folds - 1).to_numpy(dtype=np.int16)
        result[index] = assigned
    return result


def make_split_manifest(data: DatasetView, config: dict) -> pd.DataFrame:
    protocol = config["split_protocol"]
    n_folds = int(config["n_folds"])
    seed = int(config["seed"])
    if protocol == "source_ood":
        folds = balanced_group_folds(data.metadata["source_group"], n_folds, seed)
        split_group = data.metadata["source_group"].astype(str)
    elif protocol == "waterbody_ood":
        folds = balanced_group_folds(data.metadata["waterbody_group"], n_folds, seed)
        split_group = data.metadata["waterbody_group"].astype(str)
    elif protocol == "temporal_ood":
        folds = temporal_folds(data.metadata, n_folds)
        split_group = data.metadata["source_group"].astype(str)
    else:
        raise ValueError(f"unknown split protocol: {protocol}")

    test_fold = int(config["test_fold"])
    validation_fold = int(config["validation_fold"])
    role = np.full(len(folds), "train", dtype=object)
    role[folds == validation_fold] = "validation"
    role[folds == test_fold] = "test"
    manifest = pd.DataFrame(
        {
            "record_id": data.metadata["record_id"].astype(str),
            "protocol": protocol,
            "fold": folds,
            "role": role,
            "split_group": split_group,
            "source_group": data.metadata["source_group"].astype(str),
            "waterbody_group": data.metadata["waterbody_group"].astype(str),
            "sample_date": data.metadata["sample_datetime"],
        }
    )
    validate_split_manifest(manifest, n_folds, test_fold, validation_fold)
    return manifest


def validate_split_manifest(
    manifest: pd.DataFrame, n_folds: int, test_fold: int, validation_fold: int
) -> None:
    if manifest["record_id"].duplicated().any():
        raise ValueError("split manifest has duplicate record IDs")
    if not set(manifest["fold"].unique()).issubset(set(range(n_folds))):
        raise ValueError("split manifest contains invalid fold IDs")
    if set(manifest["role"].unique()) != {"train", "validation", "test"}:
        raise ValueError("all three split roles must be non-empty")
    if (manifest.loc[manifest["fold"] == test_fold, "role"] != "test").any():
        raise ValueError("test fold role mismatch")
    if (manifest.loc[manifest["fold"] == validation_fold, "role"] != "validation").any():
        raise ValueError("validation fold role mismatch")

    protocol = str(manifest["protocol"].iloc[0])
    if protocol in {"source_ood", "waterbody_ood"}:
        role_sets = {role: set(part["split_group"]) for role, part in manifest.groupby("role")}
        if role_sets["train"] & role_sets["validation"]:
            raise ValueError("train/validation group leakage")
        if role_sets["train"] & role_sets["test"]:
            raise ValueError("train/test group leakage")
        if role_sets["validation"] & role_sets["test"]:
            raise ValueError("validation/test group leakage")
    else:
        dated = manifest.dropna(subset=["sample_date"])
        for _, source in dated.groupby("source_group"):
            train = source.loc[source["role"] == "train", "sample_date"]
            validation = source.loc[source["role"] == "validation", "sample_date"]
            test = source.loc[source["role"] == "test", "sample_date"]
            if len(train) and len(validation) and train.max() > validation.min():
                raise ValueError("temporal leakage: training date after validation date")
            if len(validation) and len(test) and validation.max() > test.min():
                raise ValueError("temporal leakage: validation date after test date")


def split_indices(manifest: pd.DataFrame) -> SplitIndices:
    return SplitIndices(
        train=np.flatnonzero(manifest["role"].to_numpy() == "train"),
        validation=np.flatnonzero(manifest["role"].to_numpy() == "validation"),
        test=np.flatnonzero(manifest["role"].to_numpy() == "test"),
    )


def split_summary(manifest: pd.DataFrame) -> dict:
    rows: dict[str, dict] = {}
    for role, part in manifest.groupby("role", sort=False):
        rows[str(role)] = {
            "rows": len(part),
            "sources": int(part["source_group"].nunique()),
            "waterbodies": int(part["waterbody_group"].nunique()),
            "date_min": None
            if part["sample_date"].notna().sum() == 0
            else part["sample_date"].min().date().isoformat(),
            "date_max": None
            if part["sample_date"].notna().sum() == 0
            else part["sample_date"].max().date().isoformat(),
        }
    return {"protocol": str(manifest["protocol"].iloc[0]), "roles": rows}


def write_split_artifacts(manifest: pd.DataFrame, directory: str | Path) -> None:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(directory / "split_manifest.csv", index=False, encoding="utf-8-sig")
    (directory / "split_summary.json").write_text(
        json.dumps(split_summary(manifest), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def inner_group_folds(metadata: pd.DataFrame, n_folds: int, seed: int) -> np.ndarray:
    """Use waterbody groups for leakage-safe stacking inside the outer training set."""
    return balanced_group_folds(metadata["waterbody_group"], n_folds=n_folds, seed=seed)
