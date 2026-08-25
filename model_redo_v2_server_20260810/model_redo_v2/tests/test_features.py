from __future__ import annotations

import pytest

from cmadre.features import assert_no_leakage, panel_features, resolve_features


def test_registered_panels_have_no_forbidden_features() -> None:
    for panel in ("core_field", "static_context", "bloom_augmented", "hybrid"):
        features = panel_features(panel)
        assert len(features) == len(set(features))
        assert_no_leakage(features)


def test_leakage_guard_rejects_targets_and_ids() -> None:
    with pytest.raises(ValueError):
        assert_no_leakage(["ph", "target_ug_l"])
    with pytest.raises(ValueError):
        assert_no_leakage(["record_id"])


def test_resolve_features_preserves_registered_order() -> None:
    available, missing = resolve_features("core_field", ["ph", "month_cos", "month_sin"])
    assert available == ["month_sin", "month_cos", "ph"]
    assert "water_temp_c_best" in missing
