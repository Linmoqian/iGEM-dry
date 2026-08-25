"""Full data-quality audit for the CMADRE review rounds (R9+).

Read-only against model tables. Produces:
  references/review_data_audit.json     - machine-readable audit
  tmp_code/_audit_output_summary.txt    - human-readable summary

Not a model training script. No model-fitting here.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data" / "model_tables"
OUT = ROOT / "references" / "review_data_audit.json"
SUM = Path(__file__).resolve().parent / "_audit_output_summary.txt"

CORE_FIELD = [
    "month_sin", "month_cos", "water_temp_c_best", "do_mg_l", "ph",
    "turbidity_ntu", "conductivity_us_cm", "tn_mg_l", "tp_mg_l",
    "ammonia_n_mg_l", "nitrate_n_mg_l", "nitrite_n_mg_l",
    "nitrate_nitrite_n_mg_l", "doc_mg_l", "toc_mg_l", "tss_mg_l",
    "secchi_m", "sample_depth_m", "max_depth_m", "silica_mg_l",
]
BLOOM_PROXY = ["chlorophyll_a_ug_l", "cyanobacteria_cells_ml"]
STATIC_CONTEXT = [
    "month_sin", "month_cos", "latitude", "longitude", "lake_area_km2",
    "shore_length_km", "shore_development", "lake_volume_mcm",
    "lake_mean_depth_m", "lake_mean_discharge_m3_s",
    "lake_residence_time_days", "lake_elevation_m",
    "lake_watershed_area_km2", "chelsa_annual_mean_air_temp_c",
    "chelsa_warmest_month_max_temp_c", "chelsa_coldest_month_min_temp_c",
    "chelsa_annual_precip_mm", "chelsa_wettest_month_precip_mm",
    "chelsa_driest_month_precip_mm", "chelsa_precip_seasonality_cv",
    "chelsa_mean_climatic_moisture_index", "chelsa_frost_days",
    "chelsa_growing_season_length_days", "chelsa_mean_relative_humidity_pct",
    "chelsa_mean_pet_mm", "chelsa_mean_solar_radiation_w_m2",
    "chelsa_climatic_water_balance_mm", "chelsa_mean_vpd_hpa",
    "distance_to_sink_km", "distance_to_mainstem_km",
    "subbasin_area_km2", "upstream_area_km2", "endorheic_flag",
    "coastal_basin_flag", "hydrologic_order",
    "worldcover_5km_tree_cover_fraction", "worldcover_5km_shrubland_fraction",
    "worldcover_5km_grassland_fraction", "worldcover_5km_cropland_fraction",
    "worldcover_5km_built_up_fraction", "worldcover_5km_bare_sparse_fraction",
    "worldcover_5km_water_fraction",
    "worldcover_5km_herbaceous_wetland_fraction",
]

TABLES_OF_INTEREST = [
    "total_microcystins_enriched_dynamic_ready.csv",
    "total_microcystins_enriched_static_baseline_ready.csv",
    "mc_lr_enriched_dynamic_ready.csv",
    "mc_lr_enriched_static_baseline_ready.csv",
]


def quant(vals, qs=(0.5, 0.9, 0.95, 0.99, 0.999)):
    v = pd.to_numeric(vals, errors="coerce")
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return {}
    out = {"n": int(len(v)), "min": float(v.min()), "max": float(v.max())}
    for q in qs:
        out["q" + str(q)] = float(v.quantile(q))
    return out


def count_top(series, k):
    return {str(kk): int(v) for kk, v in series.value_counts().head(k).items()}


def audit_table(path: Path) -> dict:
    df = pd.read_csv(path)
    n = len(df)
    censored = df["is_censored"].fillna(0).astype(bool).to_numpy()
    target_num = pd.to_numeric(df["target_ug_l"], errors="coerce")
    exact = (~censored) & np.isfinite(target_num)
    detected = pd.to_numeric(df.get("detected"), errors="coerce")
    detected_b = np.where(np.isfinite(detected), detected > 0, exact).astype(bool)

    censor_lim = pd.to_numeric(df["censor_limit_ug_l"], errors="coerce")
    det_lim = pd.to_numeric(df["detection_limit_ug_l"], errors="coerce")
    rep_lim = pd.to_numeric(df["reporting_limit_ug_l"], errors="coerce")
    cens_has_limit = censored & (censor_lim.notna() | det_lim.notna() | rep_lim.notna())

    src = df["dataset_id"].astype(str)
    src_counts = count_top(src, 20)
    countries = df.get("country")
    country_counts = {}
    if countries is not None:
        country_counts = count_top(countries.astype(str).replace("nan", "NA").replace("None", "NA"), 12)

    date_series = pd.to_datetime(df["sample_date"], errors="coerce")
    date_span = [str(np.nanmin(date_series)), str(np.nanmax(date_series))] if date_series.notna().any() else ["", ""]

    waterbodies = df.get("waterbody_name")
    wb_unique = int(waterbodies.nunique()) if waterbodies is not None else 0
    sites = df.get("site_id")
    sites_unique = int(sites.nunique()) if sites is not None else 0

    qf = df.get("target_quality_flag")
    qf_counts = {}
    if qf is not None:
        qf_counts = count_top(qf.fillna("").astype(str), 20)

    exact_vals = df.loc[exact, "target_ug_l"]
    exact_quant = quant(exact_vals)

    extreme_mask = np.isfinite(target_num) & (target_num > 1000)
    extreme_by_src = {}
    if extreme_mask.sum() > 0:
        extreme_by_src = count_top(df.loc[extreme_mask, "dataset_id"].astype(str), 10)

    dup_groups = 0
    dup_rows = 0
    dup_key = ["dataset_id", "site_id", "sample_date"]
    if all(c in df for c in dup_key):
        g = df.groupby(dup_key, dropna=False).size()
        dup_groups = int((g > 1).sum())
        dup_rows = int(g[g > 1].sum() - (g > 1).sum())

    coverage = {}
    for panel, names in (("core_field", CORE_FIELD), ("bloom_augmented", BLOOM_PROXY), ("static_context", STATIC_CONTEXT)):
        avail = [c for c in names if c in df.columns]
        cov = {c: float(df[c].notna().mean()) for c in avail}
        coverage[panel] = {"available": len(avail),
                           "coverage": cov,
                           "all_present_rate": float(np.mean(list(cov.values()))) if cov else None}

    lab = np.log1p(pd.to_numeric(df.loc[exact, "target_ug_l"], errors="coerce"))
    sp_all = {}
    if len(lab) > 10:
        for c in CORE_FIELD + BLOOM_PROXY:
            if c in df:
                x = pd.to_numeric(df.loc[exact, c], errors="coerce")
                m = x.notna() & lab.notna()
                if m.sum() >= 30:
                    sp_all[c] = float(pd.Series(lab[m]).corr(pd.Series(x[m]), method="spearman"))

    sp_by_src = {}
    top_src = [s for s, _ in sorted(src_counts.items(), key=lambda kv: -kv[1])[:5]]
    for s in top_src:
        m_src = (df["dataset_id"].astype(str) == s) & exact
        lab_s = np.log1p(pd.to_numeric(df.loc[m_src, "target_ug_l"], errors="coerce"))
        tmp = {}
        for c in CORE_FIELD[:8] + BLOOM_PROXY:
            if c in df:
                x = pd.to_numeric(df.loc[m_src, c], errors="coerce")
                m = x.notna() & lab_s.notna()
                if m.sum() >= 30:
                    tmp[c] = float(pd.Series(lab_s[m]).corr(pd.Series(x[m]), method="spearman"))
        sp_by_src[s] = tmp

    return {
        "file": path.name,
        "n_rows": int(n),
        "n_exact_labels": int(exact.sum()),
        "n_censored": int(censored.sum()),
        "censored_with_lod": int(cens_has_limit.sum()),
        "censored_without_lod": int((censored & ~cens_has_limit).sum()),
        "n_detected_rows": int(detected_b.sum()),
        "n_sources": int(src.nunique()),
        "source_counts": src_counts,
        "country_counts": country_counts,
        "n_waterbodies": wb_unique,
        "n_sites": sites_unique,
        "date_span": date_span,
        "exact_label_quantiles": exact_quant,
        "extreme_gt1000_count": int(extreme_mask.sum()),
        "extreme_gt1000_by_source": extreme_by_src,
        "quality_flag_counts": qf_counts,
        "duplicate_site_date_groups": dup_groups,
        "duplicate_site_date_extra_rows": dup_rows,
        "feature_coverage": coverage,
        "spearman_log1p_label_vs_feature_all": sp_all,
        "spearman_log1p_label_vs_feature_top_sources": sp_by_src,
    }


def main() -> None:
    result = {}
    lines = []
    for name in TABLES_OF_INTEREST:
        aud = audit_table(TABLES / name)
        result[name] = aud
        lines.append("")
        lines.append(f"--- {name} ---")
        lines.append("n | exact | censored | censored_with_lod | sources | wb | sites | dup_groups | dup_rows")
        lines.append(f"{aud['n_rows']} | {aud['n_exact_labels']} | {aud['n_censored']} | {aud['censored_with_lod']} | "
                     f"{aud['n_sources']} | {aud['n_waterbodies']} | {aud['n_sites']} | {aud['duplicate_site_date_groups']} | {aud['duplicate_site_date_extra_rows']}")
        lines.append(f"sources: {aud['source_counts']}")
        lines.append(f"countries: {aud['country_counts']}")
        lines.append(f"date: {aud['date_span']}")
        lines.append(f"exact quantiles: {aud['exact_label_quantiles']}")
        lines.append(f"extreme>1000: {aud['extreme_gt1000_count']} by source {aud['extreme_gt1000_by_source']}")
        lines.append(f"qc flags: {aud['quality_flag_counts']}")
        for panel, cov in aud["feature_coverage"].items():
            lines.append(f"coverage {panel}: all_present={cov['all_present_rate']:.3f} available={cov['available']}")
        lines.append("spearman all (top 10 by |r|):")
        top_sp = sorted(aud["spearman_log1p_label_vs_feature_all"].items(), key=lambda kv: -abs(kv[1]))[:10]
        for c, v in top_sp:
            lines.append(f"  {c}: {v:.3f}")
        for s, tmp in aud["spearman_log1p_label_vs_feature_top_sources"].items():
            lines.append(f"  source {s}: {tmp}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    SUM.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:90]))
    print("SOURCES_END")


if __name__ == "__main__":
    main()
