"""Profile the currently processed toxin tables without modifying source data."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "model_redo" / "data" / "data_processed"
TABLE_ROOT = DATA_ROOT / "model_tables"
OUTPUT = ROOT / "model_redo_v2" / "references" / "current_data_profile.json"


def clean_scalar(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def series_counts(series: pd.Series, limit: int = 25) -> dict[str, int]:
    counts = series.fillna("<missing>").astype(str).value_counts(dropna=False).head(limit)
    return {str(k): int(v) for k, v in counts.items()}


def concentration_profile(series: pd.Series) -> dict:
    x = pd.to_numeric(series, errors="coerce")
    finite = x.dropna()
    if finite.empty:
        return {"non_null": 0}
    quantiles = finite.quantile([0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1])
    return {
        "non_null": int(finite.size),
        "zero_or_less": int((finite <= 0).sum()),
        "positive": int((finite > 0).sum()),
        "quantiles_ug_l": {str(k): float(v) for k, v in quantiles.items()},
    }


def profile_table(path: Path) -> dict:
    df = pd.read_csv(path, low_memory=False)
    result = {
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "memory_mb": round(float(df.memory_usage(deep=True).sum() / 1024**2), 3),
    }
    if "target_model_ug_l" in df:
        result["target_model"] = concentration_profile(df["target_model_ug_l"])
    if "target_ug_l" in df:
        result["target_observed"] = concentration_profile(df["target_ug_l"])
    for col in ["is_censored", "detected", "target_quality_flag", "matrix", "method", "training_tier"]:
        if col in df:
            result[f"counts_{col}"] = series_counts(df[col])
    for col in ["dataset_id", "site_id", "waterbody_name", "country"]:
        if col in df:
            result[f"unique_{col}"] = int(df[col].nunique(dropna=True))
            if col in {"dataset_id", "country"}:
                result[f"top_{col}"] = series_counts(df[col])
    if "sample_date" in df:
        dates = pd.to_datetime(df["sample_date"], errors="coerce")
        result["dated_rows"] = int(dates.notna().sum())
        result["date_min"] = None if dates.notna().sum() == 0 else dates.min().date().isoformat()
        result["date_max"] = None if dates.notna().sum() == 0 else dates.max().date().isoformat()
    if "dynamic_model_eligible" in df:
        result["dynamic_model_eligible"] = int(pd.to_numeric(df["dynamic_model_eligible"], errors="coerce").fillna(0).astype(bool).sum())
    if "static_baseline_eligible" in df:
        result["static_baseline_eligible"] = int(pd.to_numeric(df["static_baseline_eligible"], errors="coerce").fillna(0).astype(bool).sum())
    feature_columns = [
        "water_temp_c_best", "water_temp_c", "do_mg_l", "ph", "turbidity_ntu",
        "conductivity_us_cm", "tn_mg_l", "tp_mg_l", "ammonia_n_mg_l",
        "nitrate_n_mg_l", "nitrate_nitrite_n_mg_l", "doc_mg_l", "toc_mg_l",
        "tss_mg_l", "chlorophyll_a_ug_l", "secchi_m", "silica_mg_l",
        "cyanobacteria_cells_ml", "lswt_current_c", "lake_area_km2",
        "lake_mean_depth_m", "chelsa_annual_mean_air_temp_c",
        "hydrobasins_id", "worldcover_5km_cropland_fraction",
    ]
    result["feature_coverage"] = {
        col: {
            "non_null": int(df[col].notna().sum()),
            "fraction": round(float(df[col].notna().mean()), 6),
        }
        for col in feature_columns
        if col in df
    }
    return result


def main() -> None:
    table_names = [
        "total_microcystins_enriched_all.csv",
        "total_microcystins_enriched_dynamic_ready.csv",
        "total_microcystins_enriched_static_baseline_ready.csv",
        "mc_lr_enriched_all.csv",
        "mc_lr_enriched_dynamic_ready.csv",
        "mc_lr_enriched_static_baseline_ready.csv",
        "microcystin_detection_classification.csv",
        "china_covariates.csv",
        "taihu_multimodal_covariates.csv",
        "taihu_quarterly_multimodal_covariates.csv",
    ]
    report = {
        "source_root": str(DATA_ROOT.relative_to(ROOT)).replace("\\", "/"),
        "tables": {},
    }
    for name in table_names:
        path = TABLE_ROOT / name
        if path.exists():
            report["tables"][name] = profile_table(path)

    validation_path = DATA_ROOT / "reports" / "validation_summary.json"
    if validation_path.exists():
        report["validation_summary"] = json.loads(validation_path.read_text(encoding="utf-8"))
    processing_path = DATA_ROOT / "reports" / "processing_summary.json"
    if processing_path.exists():
        report["processing_summary"] = json.loads(processing_path.read_text(encoding="utf-8"))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
