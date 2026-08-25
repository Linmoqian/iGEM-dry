"""Pre-registered feature panels and leakage guards."""

from __future__ import annotations

from collections.abc import Iterable

CORE_FIELD = [
    "month_sin",
    "month_cos",
    "water_temp_c_best",
    "do_mg_l",
    "ph",
    "turbidity_ntu",
    "conductivity_us_cm",
    "tn_mg_l",
    "tp_mg_l",
    "ammonia_n_mg_l",
    "nitrate_n_mg_l",
    "nitrite_n_mg_l",
    "nitrate_nitrite_n_mg_l",
    "doc_mg_l",
    "toc_mg_l",
    "tss_mg_l",
    "secchi_m",
    "sample_depth_m",
    "max_depth_m",
    "silica_mg_l",
]

BLOOM_PROXY = [
    "chlorophyll_a_ug_l",
    "cyanobacteria_cells_ml",
]

STATIC_CONTEXT = [
    "month_sin",
    "month_cos",
    "latitude",
    "longitude",
    "lake_area_km2",
    "shore_length_km",
    "shore_development",
    "lake_volume_mcm",
    "lake_mean_depth_m",
    "lake_mean_discharge_m3_s",
    "lake_residence_time_days",
    "lake_elevation_m",
    "lake_watershed_area_km2",
    "chelsa_annual_mean_air_temp_c",
    "chelsa_warmest_month_max_temp_c",
    "chelsa_coldest_month_min_temp_c",
    "chelsa_annual_precip_mm",
    "chelsa_wettest_month_precip_mm",
    "chelsa_driest_month_precip_mm",
    "chelsa_precip_seasonality_cv",
    "chelsa_mean_climatic_moisture_index",
    "chelsa_frost_days",
    "chelsa_growing_season_length_days",
    "chelsa_mean_relative_humidity_pct",
    "chelsa_mean_pet_mm",
    "chelsa_mean_solar_radiation_w_m2",
    "chelsa_climatic_water_balance_mm",
    "chelsa_mean_vpd_hpa",
    "distance_to_sink_km",
    "distance_to_mainstem_km",
    "subbasin_area_km2",
    "upstream_area_km2",
    "endorheic_flag",
    "coastal_basin_flag",
    "hydrologic_order",
    "worldcover_5km_tree_cover_fraction",
    "worldcover_5km_shrubland_fraction",
    "worldcover_5km_grassland_fraction",
    "worldcover_5km_cropland_fraction",
    "worldcover_5km_built_up_fraction",
    "worldcover_5km_bare_sparse_fraction",
    "worldcover_5km_water_fraction",
    "worldcover_5km_herbaceous_wetland_fraction",
]

FORBIDDEN_EXACT = {
    "record_id",
    "source_file",
    "source_row",
    "dataset_id",
    "site_id",
    "waterbody_name",
    "target_raw",
    "target_ug_l",
    "target_model_ug_l",
    "target_kind",
    "task",
    "detected",
    "is_censored",
    "censor_limit_ug_l",
    "detection_limit_ug_l",
    "reporting_limit_ug_l",
    "qualifier",
    "target_quality_flag",
    "model_eligible",
    "dynamic_model_eligible",
    "static_baseline_eligible",
}

FORBIDDEN_PREFIXES = ("target_", "prediction_", "risk_")


def panel_features(panel: str) -> list[str]:
    if panel == "core_field":
        return list(CORE_FIELD)
    if panel == "static_context":
        return list(STATIC_CONTEXT)
    if panel == "bloom_augmented":
        return _deduplicate([*CORE_FIELD, *BLOOM_PROXY])
    if panel == "hybrid":
        return _deduplicate([*CORE_FIELD, *BLOOM_PROXY, *STATIC_CONTEXT])
    raise ValueError(f"unknown feature panel: {panel}")


def _deduplicate(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def assert_no_leakage(features: Iterable[str]) -> None:
    violations = [
        feature
        for feature in features
        if feature in FORBIDDEN_EXACT or any(feature.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
    ]
    if violations:
        raise ValueError(f"forbidden/leaky features selected: {sorted(set(violations))}")


def resolve_features(panel: str, columns: Iterable[str]) -> tuple[list[str], list[str]]:
    available_columns = set(columns)
    requested = panel_features(panel)
    available = [name for name in requested if name in available_columns]
    missing = [name for name in requested if name not in available_columns]
    assert_no_leakage(available)
    if not available:
        raise ValueError(f"none of the features for panel {panel!r} are available")
    return available, missing
