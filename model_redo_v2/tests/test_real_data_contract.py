from __future__ import annotations

from cmadre.config import load_config
from cmadre.data import load_dataset
from cmadre.features import assert_no_leakage
from cmadre.splits import make_split_manifest


def test_copied_total_mc_data_contract_and_source_split() -> None:
    config = load_config(overrides={"target": "total_microcystins", "panel": "core_field"})
    data = load_dataset(config)
    assert len(data.X) > 20_000
    assert (~data.labels.exact).sum() > 10_000
    assert_no_leakage(data.feature_names)
    manifest = make_split_manifest(data, config)
    train_sources = set(manifest.loc[manifest.role == "train", "source_group"])
    test_sources = set(manifest.loc[manifest.role == "test", "source_group"])
    assert not train_sources & test_sources
