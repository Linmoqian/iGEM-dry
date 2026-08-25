from __future__ import annotations

import numpy as np
import pandas as pd

from cmadre.splits import balanced_group_folds, inner_group_folds, temporal_folds


def test_balanced_group_folds_are_deterministic_and_group_exclusive() -> None:
    groups = pd.Series([f"g{i // 3}" for i in range(90)])
    first = balanced_group_folds(groups, n_folds=5, seed=42)
    second = balanced_group_folds(groups, n_folds=5, seed=42)
    np.testing.assert_array_equal(first, second)
    for group in groups.unique():
        assert len(np.unique(first[groups.to_numpy() == group])) == 1
    sizes = np.bincount(first, minlength=5)
    assert sizes.max() - sizes.min() <= 3


def test_temporal_fold_zero_is_newest_and_no_date_crosses_fold() -> None:
    metadata = pd.DataFrame(
        {
            "source_group": ["a"] * 20 + ["b"] * 20,
            "sample_datetime": list(pd.date_range("2020-01-01", periods=20)) * 2,
        }
    )
    folds = temporal_folds(metadata, n_folds=5)
    metadata["fold"] = folds
    for _, source in metadata.groupby("source_group"):
        assert (
            source.loc[source.fold == 0, "sample_datetime"].min()
            > source.loc[source.fold == 1, "sample_datetime"].max()
        )
        assert source.groupby("sample_datetime")["fold"].nunique().max() == 1


def test_inner_source_ood_folds_hold_out_whole_sources() -> None:
    metadata = pd.DataFrame(
        {
            "source_group": ["a", "a", "b", "b", "c", "c"],
            "waterbody_group": [f"w{i}" for i in range(6)],
        }
    )
    folds = inner_group_folds(metadata, n_folds=3, seed=42, outer_protocol="source_ood")
    metadata["fold"] = folds
    assert metadata.groupby("source_group")["fold"].nunique().max() == 1
    assert len(np.unique(folds)) == 3
