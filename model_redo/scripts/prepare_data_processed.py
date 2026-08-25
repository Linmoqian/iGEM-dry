"""Prepare modeling-ready CSV tables without modifying raw data.

The project has two related targets:
* total microcystin (MCX/MC total) for the main regression and risk model;
* explicit microcystin-LR (MC-LR) for validation/calibration.

This script reads CSV files only.  Source files are never overwritten.  Each
output retains a source path, a stable record id, the reported target (when
available), censoring/LOD information, and a modelling value that uses half
the reported detection limit only when the source explicitly identifies a
censored observation and supplies a limit.  The rule is recorded in
``imputation_rule`` and is not applied to ordinary missing values.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXTERNAL = ROOT / "data" / "external_raw"
OUT = ROOT / "data" / "data_processed"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


CANONICAL = [
    "record_id",
    "dataset_id",
    "task_group",
    "source_scope",
    "source_file",
    "source_row_number",
    "waterbody_name",
    "site_id",
    "sample_date",
    "year",
    "month",
    "latitude",
    "longitude",
    "depth_m",
    "secchi_m",
    "water_temp_c",
    "do_mgL",
    "ph",
    "turbidity_ntu",
    "chla_ugL",
    "pc_ugL",
    "tn_mgL",
    "tp_mgL",
    "no3_no2_mgL",
    "nh3_mgL",
    "total_mc_raw",
    "total_mc_ugL",
    "total_mc_model_ugL",
    "mclr_raw",
    "mclr_ugL",
    "mclr_model_ugL",
    "mc_detected",
    "censored_flag",
    "lod_ugL",
    "target_observed",
    "target_model_available",
    "target_type",
    "target_unit",
    "imputation_rule",
    "quality_flag",
    "parameter_name",
    "measurement_fraction",
    "prediction_value",
    "prediction_unit",
    "risk_probability",
    "notes",
]


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Read a CSV with conservative encoding fallbacks."""
    last: Optional[Exception] = None
    for enc in ("utf-8-sig", "utf-8", "gb18030", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False, **kwargs)
        except Exception as exc:  # pragma: no cover - encoding dependent
            last = exc
    raise RuntimeError(f"cannot read CSV: {path}: {last}")


def norm_col(c: object) -> str:
    return re.sub(r"\s+", " ", str(c).replace("\ufeff", "").strip()).lower()


def find_col(df: pd.DataFrame, candidates: Sequence[str], contains: bool = True) -> Optional[str]:
    cols = list(df.columns)
    normalized = {norm_col(c): c for c in cols}
    for candidate in candidates:
        key = norm_col(candidate)
        if key in normalized:
            return normalized[key]
    if contains:
        for candidate in candidates:
            key = norm_col(candidate)
            for n, c in normalized.items():
                if key and key in n:
                    return c
    return None


def series(df: pd.DataFrame, candidates: Sequence[str], default=np.nan) -> pd.Series:
    col = find_col(df, candidates)
    if col is None:
        return pd.Series(default, index=df.index)
    return df[col]


def as_number(x: object) -> float:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    s = str(x).strip().replace("\u00a0", " ")
    if not s or s.lower() in {"nan", "na", "n/a", "null", "none", "--", "-", "ns", "nm", "nd", "bdl"}:
        return np.nan
    s = s.replace(",", ".")
    # Thousands separators are uncommon in concentration fields; only remove
    # them when a decimal point is not present after the replacement.
    if s.count(".") > 1:
        s = s.replace(".", "", s.count(".") - 1)
    m = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", s)
    return float(m.group(0)) if m else np.nan


def parse_measure(value: object, qualifier: object = None, lod: object = None) -> tuple[float, float, bool, str]:
    """Return (reported numeric, limit, censored, raw text).

    A censored string such as ``<0.1`` contributes a limit but not a reported
    measurement.  A numeric result with a '<' qualifier is treated as
    censored while preserving the numeric limit.
    """
    raw = "" if value is None else str(value).strip()
    q = "" if qualifier is None else str(qualifier).strip()
    text = f"{raw} {q}".lower()
    limit = as_number(lod)
    censored = bool(re.search(r"(^|[\s<])<|below|not detected|non[- ]?detect|\bnd\b|\bmdl\b|\bldl\b|\bbdl\b", text))
    val = as_number(value)
    if raw and raw.startswith("<"):
        limit = val if not np.isnan(val) else limit
        val = np.nan
    # USGS HAB tables use negative sentinel values such as -0.15 for <0.15
    # and -500 for an unavailable result. Concentrations cannot be negative.
    if not np.isnan(val) and val < 0:
        if censored:
            limit = abs(val) if np.isnan(limit) or limit < 0 else limit
        val = np.nan
    if not np.isnan(limit) and limit < 0:
        limit = abs(limit)
    if censored and np.isnan(limit) and not np.isnan(val):
        limit = val
        # Values accompanied only by a qualifier are limits, not observations.
        if re.search(r"below|not detected|non[- ]?detect|\bnd\b|\bmdl\b|\bldl\b|\bbdl\b", text):
            val = np.nan
    return val, limit, censored, raw


def numeric_series(values: Iterable[object]) -> pd.Series:
    return pd.Series([as_number(v) for v in values])


def clean_date(values: Iterable[object], dayfirst: bool = False) -> pd.Series:
    # Materialize values so a filtered source frame's original index cannot
    # align against the fresh canonical frame and create silent date gaps.
    s = pd.Series(list(values))
    try:
        return pd.to_datetime(s, errors="coerce", format="mixed", dayfirst=dayfirst)
    except TypeError:  # older pandas
        return pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)


def empty_frame(n: int) -> pd.DataFrame:
    out = pd.DataFrame({c: [np.nan] * n for c in CANONICAL})
    for c in ["record_id", "dataset_id", "task_group", "source_scope", "source_file", "waterbody_name", "site_id", "sample_date", "total_mc_raw", "mclr_raw", "target_type", "target_unit", "imputation_rule", "quality_flag", "parameter_name", "measurement_fraction", "prediction_unit", "notes"]:
        out[c] = pd.Series([None] * n, dtype="string")
    return out


def base_frame(dataset_id: str, task_group: str, scope: str, source_file: str, n: int) -> pd.DataFrame:
    out = empty_frame(n)
    out["dataset_id"] = dataset_id
    out["task_group"] = task_group
    out["source_scope"] = scope
    out["source_file"] = source_file
    out["source_row_number"] = np.arange(1, n + 1)
    out["record_id"] = [f"{dataset_id}:{i}" for i in range(1, n + 1)]
    return out


def set_common(out: pd.DataFrame, df: pd.DataFrame, mapping: dict[str, Sequence[str]]) -> None:
    for dest, candidates in mapping.items():
        out[dest] = series(df, candidates).to_numpy()


def set_dates(out: pd.DataFrame, values: Iterable[object], dayfirst: bool = False) -> None:
    d = clean_date(values, dayfirst=dayfirst)
    out["sample_date"] = d.dt.strftime("%Y-%m-%d")
    out["year"] = d.dt.year
    out["month"] = d.dt.month


def target_from_values(
    out: pd.DataFrame,
    values: Iterable[object],
    qualifiers: Iterable[object] | None = None,
    lod_values: Iterable[object] | None = None,
    target: str = "total",
    use_half_lod: bool = True,
    detected: Iterable[object] | None = None,
) -> None:
    vals = list(values)
    qs = list(qualifiers) if qualifiers is not None else [None] * len(vals)
    lods = list(lod_values) if lod_values is not None else [None] * len(vals)
    parsed = [parse_measure(v, q, l) for v, q, l in zip(vals, qs, lods)]
    measured = pd.Series([p[0] for p in parsed], index=out.index, dtype="float64")
    limits = pd.Series([p[1] for p in parsed], index=out.index, dtype="float64")
    cens = pd.Series([p[2] for p in parsed], index=out.index, dtype="boolean").fillna(False)
    raw = pd.Series([p[3] for p in parsed], index=out.index, dtype="string")
    # A numeric field accompanied by ND/BDL/< is a reporting limit, not an
    # observed concentration. Keep the raw text and expose the half-LOD value
    # separately for model sensitivity analyses.
    measured = measured.mask(cens, np.nan)
    model = measured.copy()
    imputation = pd.Series("none", index=out.index, dtype="string")
    if use_half_lod:
        mask = measured.isna() & cens & limits.notna()
        model.loc[mask] = limits.loc[mask] / 2.0
        imputation.loc[mask] = "lod_half"
    if target == "total":
        out["total_mc_raw"] = raw
        out["total_mc_ugL"] = measured
        out["total_mc_model_ugL"] = model
        out["lod_ugL"] = limits
    elif target == "mclr":
        out["mclr_raw"] = raw
        out["mclr_ugL"] = measured
        out["mclr_model_ugL"] = model
        out["lod_ugL"] = limits
    out["censored_flag"] = cens
    out["imputation_rule"] = imputation
    out["target_observed"] = measured.notna()
    out["target_model_available"] = model.notna()
    if detected is not None:
        det = pd.Series(list(detected), index=out.index)
        out["mc_detected"] = det.astype("string")
    else:
        out["mc_detected"] = np.where(measured.notna(), (measured > 0).astype("Int64"), pd.NA)
    out["target_type"] = target
    out["target_unit"] = "ug/L"


def finalize(out: pd.DataFrame) -> pd.DataFrame:
    # Ensure all canonical columns exist, and normalize the common numeric
    # fields without coercing arbitrary source metadata.
    for c in CANONICAL:
        if c not in out:
            out[c] = np.nan
    for c in [
        "latitude", "longitude", "depth_m", "secchi_m", "water_temp_c", "do_mgL", "ph",
        "turbidity_ntu", "chla_ugL", "pc_ugL", "tn_mgL", "tp_mgL", "no3_no2_mgL", "nh3_mgL",
        "total_mc_ugL", "total_mc_model_ugL", "mclr_ugL", "mclr_model_ugL", "lod_ugL",
        "prediction_value", "risk_probability",
    ]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out["sample_date"] = out["sample_date"].astype("string")
    # Recalculate year/month only when a parsed date is available.
    d = pd.to_datetime(out["sample_date"], errors="coerce")
    out["year"] = out["year"].where(out["year"].notna(), d.dt.year)
    out["month"] = out["month"].where(out["month"].notna(), d.dt.month)
    out["censored_flag"] = out["censored_flag"].fillna(False).astype(bool)
    out["target_observed"] = out["target_observed"].fillna(False).astype(bool)
    out["target_model_available"] = out["target_model_available"].fillna(False).astype(bool)
    # Flag extreme values for review without deleting or clipping them.  The
    # threshold is deliberately conservative because bloom scum samples can
    # exceed ordinary water-column concentrations.
    target_values = out["total_mc_ugL"].combine_first(out["mclr_ugL"])
    high = target_values > 1000
    qf = out["quality_flag"].astype("string")
    qf.loc[high & qf.isna()] = "high_concentration_review"
    out["quality_flag"] = qf
    return out[CANONICAL]


def path_one(root: Path, pattern: str) -> Path:
    matches = sorted(root.rglob(pattern))
    if not matches:
        raise FileNotFoundError(f"missing CSV for pattern {pattern} under {root}")
    return matches[0]


def load_lake_erie() -> pd.DataFrame:
    p = path_one(RAW, "Lake_Erie_全湖采样数据_2013-2025.csv")
    df = read_csv(p)
    out = base_frame("lake_erie_full", "total_mc_training", "raw", str(p), len(df))
    set_common(out, df, {
        "waterbody_name": ["Site name"], "site_id": ["ID#", "Site name"],
        "latitude": ["Lat"], "longitude": ["Long"], "depth_m": ["Depth (m)"],
        "secchi_m": ["Secchi (m)"], "water_temp_c": ["Water Temp at 1 meter (C)"],
        "chla_ugL": ["Chlorophyll"], "tn_mgL": ["TN"], "tp_mgL": ["TP"],
        "no3_no2_mgL": ["Nitrate+NO2"], "nh3_mgL": ["Ammonium"],
    })
    set_dates(out, series(df, ["Date"]))
    target = find_col(df, ["Total Microcystins"])
    target_from_values(out, df[target] if target else [None] * len(df), target="total", use_half_lod=True)
    out["notes"] = "Lake Erie whole-lake sampling; censored values use half reported limit in *_model_ugL."
    return finalize(out)


def load_erie_sb_weekly() -> pd.DataFrame:
    p = path_one(RAW, "SB_周监测数据.csv")
    df = read_csv(p)
    out = base_frame("lake_erie_sb_weekly", "total_mc_training", "raw", str(p), len(df))
    set_common(out, df, {"site_id": ["Site"], "waterbody_name": ["Site"], "latitude": ["Lat_deg"], "longitude": ["Long_deg"],
                         "depth_m": ["Sample_Depth_m"], "secchi_m": ["Secchi_Depth_m"], "water_temp_c": ["Temp_C"],
                         "do_mgL": ["DO_mgL-1"], "turbidity_ntu": ["Turbidity_NTU"], "chla_ugL": ["Extracted_CHLa_ugL-1"]})
    set_dates(out, series(df, ["Date"]))
    part = series(df, ["Particulate_Microcystin_ugL-1"])
    diss = series(df, ["Dissolved_Microcystin_ugL-1"])
    pvals = [parse_measure(v)[0] for v in part]
    dvals = [parse_measure(v)[0] for v in diss]
    plods = [parse_measure(v)[1] for v in part]
    dlods = [parse_measure(v)[1] for v in diss]
    pc = [parse_measure(v)[2] for v in part]
    dc = [parse_measure(v)[2] for v in diss]
    measured = pd.Series(pvals, index=out.index) + pd.Series(dvals, index=out.index)
    # If only one component is available, retain it. If one component is
    # censored, the total is censored and remains missing in measured target.
    measured = measured.where(~pd.Series(pc, index=out.index) & ~pd.Series(dc, index=out.index))
    measured = measured.fillna(pd.Series(pvals, index=out.index)).where(pd.Series(dvals, index=out.index).isna(), measured)
    limits = pd.Series(plods, index=out.index).fillna(0) + pd.Series(dlods, index=out.index).fillna(0)
    limits = limits.replace(0, np.nan)
    cens = pd.Series(pc, index=out.index) | pd.Series(dc, index=out.index)
    model = measured.copy(); mask = measured.isna() & cens & limits.notna(); model.loc[mask] = limits.loc[mask] / 2
    out["total_mc_raw"] = (part.astype("string") + ";" + diss.astype("string"))
    out["total_mc_ugL"] = measured
    out["total_mc_model_ugL"] = model
    out["lod_ugL"] = limits
    out["censored_flag"] = cens
    out["imputation_rule"] = np.where(mask, "lod_half", "none")
    out["target_observed"] = measured.notna()
    out["target_model_available"] = model.notna()
    out["target_type"] = "total"; out["target_unit"] = "ug/L"; out["parameter_name"] = "particulate+dissolved microcystin"
    out["notes"] = "Particulate and dissolved components; no universal missing-value imputation."
    return finalize(out)


def load_esp() -> pd.DataFrame:
    p = path_one(RAW, "ESP_传感器部署数据.csv")
    df = read_csv(p)
    out = base_frame("erie_esp_sensor", "sensor_validation", "raw", str(p), len(df))
    set_common(out, df, {"site_id": ["Station"], "depth_m": ["depth"], "lod_ugL": ["LLOD"], "waterbody_name": ["Station"]})
    set_dates(out, series(df, ["Date"]))
    target_from_values(out, series(df, ["MC ug L-1"]), lod_values=series(df, ["LLOD"]), target="total", use_half_lod=True)
    out["notes"] = "Engineering-bacteria/ESP sensor deployment; retained as validation/calibration, not pooled with field surveys."
    return finalize(out)


def load_habs_training() -> pd.DataFrame:
    p = path_one(RAW, "HABs_模型训练数据.csv")
    df = read_csv(p)
    out = base_frame("habs_nla_driver_training", "total_mc_training", "raw", str(p), len(df))
    set_common(out, df, {"site_id": ["SITE_ID"], "waterbody_name": ["SITE_ID"], "latitude": ["LAT_DD83"], "longitude": ["LON_DD83"],
                         "depth_m": ["MAXDEPTH"], "water_temp_c": ["TEMPERATURE"], "do_mgL": ["DO_SURF"], "ph": ["PH"],
                         "turbidity_ntu": ["TURB"], "chla_ugL": ["CHLA_RESULT"], "tn_mgL": ["NTL"], "tp_mgL": ["PTL"],
                         "no3_no2_mgL": ["NITRATE_N"], "nh3_mgL": ["AMMONIA_N"]})
    set_dates(out, series(df, ["DATE_COL"]))
    target_from_values(out, series(df, ["MICX"]), detected=series(df, ["MICX_DET"]), target="total", use_half_lod=False)
    out["notes"] = "NLA driver-factor table; MICX is observed only where supplied; prediction output is kept separately."
    return finalize(out)


def load_nla(year: int) -> pd.DataFrame:
    patterns = {2012: "270_NLA_2012_Algal_Toxins_-_Data_(CSV)_(csv).csv", 2017: "499_NLA_2017_Algal_Toxin_-_Data_(CSV)_(csv).csv", 2022: "661_NLA_2022_Algal_Toxin_-_Data_(csv).csv"}
    p = path_one(RAW, patterns[year]); df = read_csv(p)
    if year == 2012:
        work = df.copy(); vals = series(work, ["MICX_RESULT"]); q = series(work, ["MICX_FLAG"]); lod = series(work, ["MICX_MDL", "MICX_RL"]); detected = None
    else:
        work = df[df[find_col(df, ["ANALYTE"])].astype("string").str.upper().eq("MICX")].copy()
        vals = series(work, ["RESULT"]); q = series(work, ["NARS_FLAG", "QA_FLAG"]); lod = series(work, ["MDL", "RL"]); detected = q
    out = base_frame(f"nla_{year}_microcystin", "total_mc_training", "raw", str(p), len(work))
    set_common(out, work, {"site_id": ["SITE_ID"], "waterbody_name": ["SITE_ID"], "latitude": ["LAT_DD83"], "longitude": ["LON_DD83"]})
    set_dates(out, series(work, ["DATE_COL"]))
    target_from_values(out, vals, qualifiers=q, lod_values=lod, target="total", use_half_lod=True, detected=detected)
    out["parameter_name"] = "MICX"; out["notes"] = f"NLA {year} algal-toxin observations filtered to MICX; censored flags retained."
    return finalize(out)


def load_ncca(year: int = 2015) -> pd.DataFrame:
    if year == 2015:
        p = path_one(RAW, "371_NCCA_2015_Microcystin_Great_Lakes_-_Data_(CSV)_(csv).csv")
        df = read_csv(p)
        vals = series(df, ["AVG_CONC"]); q = series(df, ["NARS_FLAG", "CONDITION_CODE"]); lod = series(df, ["MDL", "LOWER_RL", "UPPER_RL"])
    else:
        p = path_one(RAW, "587_NCCA_2020_Cyanotoxin_-_data_(csv).csv")
        df0 = read_csv(p); ac = find_col(df0, ["ANALYTE"]); df = df0[df0[ac].astype("string").str.upper().eq("MICX")].copy()
        vals = series(df, ["AVG_CONC", "RESULT"]); q = series(df, ["NARS_FLAG", "CONDITION_CODE"]); lod = series(df, ["RL", "MDL"])
    out = base_frame(f"ncca_{year}_microcystin", "total_mc_training", "raw", str(p), len(df))
    set_common(out, df, {"site_id": ["SITE_ID"], "waterbody_name": ["SITE_ID"], "latitude": ["LAT_DD83"], "longitude": ["LON_DD83"]})
    set_dates(out, series(df, ["DATE_COL"]))
    target_from_values(out, vals, qualifiers=q, lod_values=lod, target="total", use_half_lod=(year == 2020), detected=q)
    out["parameter_name"] = "MICX"; out["notes"] = "NCCA concentration field; AVG_CONC is used when laboratory RESULT is absent."
    return finalize(out)


def load_epacyan() -> pd.DataFrame:
    p = EXTERNAL / "EPA_CyAN_NLA_Microcystin_Model" / "HABsRisk_CyAN-NLA_ModelData.csv"
    df = read_csv(p)
    out = base_frame("epa_cyan_nla_modeldata", "auxiliary_duplicate_risk", "external_raw", str(p), len(df))
    set_common(out, df, {"site_id": ["SITE_ID"], "waterbody_name": ["SITE_ID"], "latitude": ["LAT_DD83"], "longitude": ["LON_DD83"], "chla_ugL": ["CHLA_RESULT"]})
    set_dates(out, series(df, ["DATE_COL"]))
    target_from_values(out, series(df, ["MICX_RESULT"]), qualifiers=series(df, ["MICX_NARS_FLAG"]), lod_values=series(df, ["MICX_RL", "MICX_MDL"]), target="total", use_half_lod=True)
    out["notes"] = "EPA CyAN model input; overlaps NLA 2007/2012 and is intentionally excluded from the merged training pool."
    return finalize(out)


def load_wqp() -> pd.DataFrame:
    p = EXTERNAL / "EPA_Water_Quality_Portal_Microcystin" / "extracted" / "result.csv"
    df = read_csv(p)
    unit_col = find_col(df, ["ResultMeasure/MeasureUnitCode"])
    value_col = find_col(df, ["ResultMeasureValue"])
    units = df[unit_col].astype("string").str.lower() if unit_col else pd.Series("", index=df.index)
    factors = pd.Series(np.nan, index=df.index, dtype="float64")
    for u, factor in {"ug/l": 1.0, "ug/l ": 1.0, "ug/liter": 1.0, "ug/litre": 1.0, "ppb": 1.0, "ng/ml": 1.0, "ng/mL": 1.0, "ng/l": 0.001}.items():
        factors.loc[units.eq(u.lower())] = factor
    keep = factors.notna()
    work = df.loc[keep].copy(); factors = factors.loc[keep]
    out = base_frame("epa_wqp_microcystin", "total_mc_training", "external_raw", str(p), len(work))
    set_common(out, work, {"site_id": ["MonitoringLocationIdentifier"], "waterbody_name": ["MonitoringLocationIdentifier"],
                           "latitude": ["Latitude"], "longitude": ["Longitude"]})
    set_dates(out, series(work, ["ActivityStartDate"]))
    q = series(work, ["ResultDetectionConditionText", "MeasureQualifierCode"])
    lod = series(work, ["DetectionQuantitationLimitMeasure/MeasureValue"])
    vals = pd.to_numeric(series(work, [value_col] if value_col else ["ResultMeasureValue"], default=np.nan), errors="coerce") * factors.to_numpy()
    lod_conv = pd.to_numeric(lod, errors="coerce") * factors.to_numpy()
    target_from_values(out, vals, qualifiers=q, lod_values=lod_conv, target="total", use_half_lod=True)
    out["parameter_name"] = "Microcystin (WQP)"; out["measurement_fraction"] = series(work, ["ResultSampleFractionText"])
    out["notes"] = "EPA WQP; retained only mass-concentration units convertible to ug/L; non-mass units excluded."
    return finalize(out)


def read_erie_field_files() -> pd.DataFrame:
    root = EXTERNAL / "NOAA_GLERL_Lake_Erie_2012_present"
    paths = [p for p in root.rglob("*.csv") if "converted" not in p.parts and "dictionary" not in p.name.lower() and "coordinate" not in p.name.lower() and re.search(r"results|sampling_results", p.name.lower())]
    frames = []
    for p in sorted(paths):
        try: df = read_csv(p)
        except Exception: continue
        part_c = find_col(df, ["particulate_microcystin", "Particulate Microcystin"])
        diss_c = find_col(df, ["dissolved_microcystin", "Dissolved Microcystin"])
        if not part_c and not diss_c: continue
        out = base_frame("noaa_glerl_erie_field", "total_mc_training", "external_raw", str(p), len(df))
        set_common(out, df, {"site_id": ["station_name", "Site"], "waterbody_name": ["station_name", "Site"], "latitude": ["lat", "Latitude"], "longitude": ["lon", "Longitude"],
                             "depth_m": ["sample_depth_m", "Sample Depth"], "secchi_m": ["secchi_depth", "Secchi Depth"], "water_temp_c": ["ctd_temp", "CTD Temperature", "Sample Temperature"],
                             "do_mgL": ["ctd_dissolved_oxygen", "CTD Dissolved Oxygen"], "turbidity_ntu": ["turbidity", "Turbidity"], "chla_ugL": ["extracted_chla", "Extracted Chlorophyll"]})
        set_dates(out, series(df, ["date", "Date"]))
        part = series(df, [part_c] if part_c else ["__missing__"]); diss = series(df, [diss_c] if diss_c else ["__missing__"])
        pv = [parse_measure(v) for v in part]; dv = [parse_measure(v) for v in diss]
        pnum = pd.Series([x[0] for x in pv], index=out.index); dnum = pd.Series([x[0] for x in dv], index=out.index)
        plim = pd.Series([x[1] for x in pv], index=out.index); dlim = pd.Series([x[1] for x in dv], index=out.index)
        cens = pd.Series([x[2] for x in pv], index=out.index) | pd.Series([x[2] for x in dv], index=out.index)
        # A measured total is valid only when each non-missing component is
        # reported; when one component is absent, retain the available one.
        measured = pnum.add(dnum, fill_value=0).where(~cens)
        measured = measured.where(pnum.notna() | dnum.notna())
        limits = plim.fillna(0).add(dlim.fillna(0)).replace(0, np.nan)
        model = pnum.fillna(plim / 2).add(dnum.fillna(dlim / 2), fill_value=0)
        model = model.where(pnum.notna() | dnum.notna() | limits.notna())
        out["total_mc_raw"] = part.astype("string") + ";" + diss.astype("string")
        out["total_mc_ugL"] = measured; out["total_mc_model_ugL"] = model; out["lod_ugL"] = limits
        out["censored_flag"] = cens; out["target_observed"] = measured.notna(); out["target_model_available"] = model.notna(); out["target_type"] = "total"; out["target_unit"] = "ug/L"
        out["imputation_rule"] = np.where(model.notna() & measured.isna() & cens, "lod_half_component", "none")
        frames.append(finalize(out))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=CANONICAL)


def read_saginaw_field_files() -> pd.DataFrame:
    root = EXTERNAL / "NOAA_GLERL_SaginawBay"
    paths = [p for p in root.rglob("*.csv") if "converted" not in p.parts and "coordinate" not in p.name.lower() and re.search(r"sampling_results|habs_20", p.name.lower())]
    frames = []
    for p in sorted(paths):
        try: df = read_csv(p)
        except Exception: continue
        pc = find_col(df, ["Particulate Microcystin", "Particulate\\nMicrocystin"]); dc = find_col(df, ["Dissolved Microcystin", "Dissolved\\nMicrocystin"])
        if not pc and not dc: continue
        # Reuse the Erie loader by normalizing column names locally.
        tmp = df.copy(); tmp.columns = [re.sub(r"\s+", " ", str(c).replace("\n", " ").strip()) for c in tmp.columns]
        pc = find_col(tmp, ["Particulate Microcystin"]); dc = find_col(tmp, ["Dissolved Microcystin"])
        out = base_frame("noaa_glerl_saginaw_field", "total_mc_training", "external_raw", str(p), len(tmp))
        set_common(out, tmp, {"site_id": ["Site"], "waterbody_name": ["Site"], "latitude": ["Latitude (decimal degrees)"], "longitude": ["Longitude (decimal degrees)"], "depth_m": ["Sample Depth (m)"], "secchi_m": ["Secchi Depth (m)"], "water_temp_c": ["CTD Temperature (°C)"], "do_mgL": ["CTD Dissolved Oxygen (mg/L)"], "turbidity_ntu": ["Turbidity (NTU)"], "chla_ugL": ["Extracted Chlorophyll a (µg/L)", "Extracted Chlorophyll"]})
        set_dates(out, series(tmp, ["Date"]))
        part = series(tmp, [pc] if pc else ["__missing__"]); diss = series(tmp, [dc] if dc else ["__missing__"])
        pv = [parse_measure(v) for v in part]; dv = [parse_measure(v) for v in diss]
        pnum = pd.Series([x[0] for x in pv], index=out.index); dnum = pd.Series([x[0] for x in dv], index=out.index); plim = pd.Series([x[1] for x in pv], index=out.index); dlim = pd.Series([x[1] for x in dv], index=out.index); cens = pd.Series([x[2] for x in pv], index=out.index) | pd.Series([x[2] for x in dv], index=out.index)
        measured = pnum.add(dnum, fill_value=0).where(~cens).where(pnum.notna() | dnum.notna()); limits = plim.fillna(0).add(dlim.fillna(0)).replace(0, np.nan); model = pnum.fillna(plim / 2).add(dnum.fillna(dlim / 2), fill_value=0).where(pnum.notna() | dnum.notna() | limits.notna())
        out["total_mc_raw"] = part.astype("string") + ";" + diss.astype("string"); out["total_mc_ugL"] = measured; out["total_mc_model_ugL"] = model; out["lod_ugL"] = limits; out["censored_flag"] = cens; out["target_observed"] = measured.notna(); out["target_model_available"] = model.notna(); out["target_type"] = "total"; out["target_unit"] = "ug/L"; out["imputation_rule"] = np.where(model.notna() & measured.isna() & cens, "lod_half_component", "none"); frames.append(finalize(out))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=CANONICAL)


def load_raw_saginaw_2008() -> pd.DataFrame:
    p = path_one(RAW, "saginaw_bay_water_quality_field_sampling_2008_2010.csv"); df = read_csv(p)
    out = base_frame("saginaw_bay_2008_2010", "total_mc_training", "raw", str(p), len(df))
    set_common(out, df, {"site_id": ["Site"], "waterbody_name": ["Site"], "latitude": ["Latitude"], "longitude": ["Longitude"], "depth_m": ["Station Depth"], "secchi_m": ["Secchi"], "water_temp_c": ["Sample Temperature"], "chla_ugL": ["Extracted Chlorophyll-a"], "tp_mgL": ["Total Phosphorus"], "no3_no2_mgL": ["Nitrate + Nitrite"]})
    set_dates(out, series(df, ["Date"])); target_from_values(out, series(df, ["Particulate Microcystin"]), target="total", use_half_lod=True); out["notes"] = "Raw Saginaw Bay 2008-2010 field table; particulate MC only."; return finalize(out)


def load_san_francisco() -> pd.DataFrame:
    p = path_one(RAW, "San Francisco Estuary cyanoHAB data 2014 to 2019_v1.csv"); df = read_csv(p)
    out = base_frame("san_francisco_estuary_cyanohab", "total_mc_training", "raw", str(p), len(df))
    set_common(out, df, {"site_id": ["DWR_Site", "EMP_Site"], "waterbody_name": ["DWR_Site"], "latitude": ["Lat"], "longitude": ["Lon"], "water_temp_c": ["field.Water.temp"], "do_mgL": ["field.DO.mgL"], "ph": ["field.pH"], "turbidity_ntu": ["field.NTU"], "chla_ugL": ["field.Chla"], "tp_mgL": ["bryte.TP.mgL"], "nh3_mgL": ["bryte.NH4.mgL"], "no3_no2_mgL": ["bryte.NO3.mgL"]})
    set_dates(out, series(df, ["Collection_Date"])); target_from_values(out, series(df, ["ucd.ppia.MC.total.ugL"]), target="total", use_half_lod=False); out["notes"] = "San Francisco Estuary field/qPCR data; target is total MC by PPIA. Signatures are not MC-LR concentration."; return finalize(out)


def load_emls() -> pd.DataFrame:
    p = path_one(RAW, "EMLSdata_10Aug_afterRev_dateformated.csv"); df = read_csv(p)
    out = base_frame("emls_europe_mclr", "mc_lr_validation", "raw", str(p), len(df))
    set_common(out, df, {"site_id": ["Lake_ID"], "waterbody_name": ["LakeName"], "latitude": ["Latitude"], "longitude": ["Longitude"], "depth_m": ["SamplingDepth_m"], "secchi_m": ["SecchiDepth_m"], "water_temp_c": ["SurfaceTemperature_C"], "tn_mgL": ["TN_mgL"], "tp_mgL": ["TP_mgL"], "no3_no2_mgL": ["NO3NO2_mgL"], "nh3_mgL": ["NH3_mgL"], "chla_ugL": ["Chlorophylla_ugL"]})
    set_dates(out, series(df, ["Date"])); target_from_values(out, series(df, ["MC_LR_ugL"]), target="mclr", use_half_lod=False); out["parameter_name"] = "MC-LR"; out["notes"] = "European multi-lake table with explicit MC-LR field; validation/calibration only."; return finalize(out)


def load_french() -> tuple[pd.DataFrame, pd.DataFrame]:
    files = sorted(EXTERNAL.glob("France_Cyanobacteria_Cyanotoxins_2021_2025/Extraction_cyanobacteries_*.csv"))
    total_frames: list[pd.DataFrame] = []; lr_frames: list[pd.DataFrame] = []
    for p in files:
        year_match = re.search(r"(20\d{2})", p.name); year_tag = year_match.group(1) if year_match else "unknown"
        df = pd.read_csv(p, sep=";", skiprows=12, encoding="latin1", low_memory=False)
        df.columns = [str(c).strip() for c in df.columns]
        pn = next(c for c in df.columns if "PARAM - Nom" in c); rv = next(c for c in df.columns if "RESULT - Valeur alphanum" in c); date_c = next(c for c in df.columns if "PLV - Date" in c); site_c = next(c for c in df.columns if "SIT - Code national" in c); name_c = next(c for c in df.columns if "SIT - Nom" in c); lat_c = next((c for c in df.columns if "Coordonnées" in c and "X" in c), None)
        # Keep one total measurement per sample, prioritising the direct ELISA
        # result over the calculated sum when both are present.
        param = df[pn].astype("string").str.strip()
        total_mask = param.str.lower().isin(["total des microcystines analysées - test elisa", "somme des microcystines analysées (calcul)"])
        lr_mask = param.str.lower().eq("microcystine-lr totale")
        key = [date_c, site_c, name_c]
        t = df.loc[total_mask].copy(); l = df.loc[lr_mask].copy()
        if len(t):
            t["_priority"] = param.loc[t.index].str.lower().map({"total des microcystines analysées - test elisa": 0, "somme des microcystines analysées (calcul)": 1}).fillna(9); t = t.sort_values("_priority").drop_duplicates(key, keep="first")
            out = base_frame(f"france_cyanotoxins_{year_tag}_total", "total_mc_training", "external_raw", str(p), len(t)); set_common(out, t, {"site_id": [site_c], "waterbody_name": [name_c]}); set_dates(out, t[date_c], dayfirst=True); target_from_values(out, t[rv], target="total", use_half_lod=True); out["parameter_name"] = t[pn].astype("string").str.strip(); out["notes"] = "French national cyanobacteria surveillance; semicolon CSV, source values in ug/L."; total_frames.append(finalize(out))
        if len(l):
            out = base_frame(f"france_cyanotoxins_{year_tag}_mclr", "mc_lr_validation", "external_raw", str(p), len(l)); set_common(out, l, {"site_id": [site_c], "waterbody_name": [name_c]}); set_dates(out, l[date_c], dayfirst=True); target_from_values(out, l[rv], target="mclr", use_half_lod=True); out["parameter_name"] = l[pn].astype("string").str.strip(); out["notes"] = "French surveillance explicit Microcystine-LR totale; censored values retain reported limits."; lr_frames.append(finalize(out))
    total = pd.concat(total_frames, ignore_index=True) if total_frames else pd.DataFrame(columns=CANONICAL); lr = pd.concat(lr_frames, ignore_index=True) if lr_frames else pd.DataFrame(columns=CANONICAL)
    return total, lr


def load_ncei_pontchartrain() -> pd.DataFrame:
    p = path_one(EXTERNAL, "*Database__s1.csv"); df = read_csv(p)
    out = base_frame("ncei_pontchartrain_2020", "total_mc_training", "external_raw", str(p), len(df))
    set_common(out, df, {"site_id": ["Site Name"], "waterbody_name": ["Site Name"], "latitude": ["Latitude"], "longitude": ["Longitude"], "depth_m": ["Depth"], "water_temp_c": ["Water Temperature"], "ph": ["pH"], "do_mgL": ["Dissolved Oxygen"], "chla_ugL": ["Chlorophyll"], "pc_ugL": ["Phycocyanin"], "tn_mgL": ["Ammonia as Nitrogen"], "no3_no2_mgL": ["Nitrate + Nitrite as Nitrogen"]}); set_dates(out, series(df, ["Datestamp"])); target_from_values(out, series(df, ["Microcystins"]), target="total", use_half_lod=True); out["notes"] = "USACE Lake Pontchartrain 2020 monitoring; converted CSV with field water quality and cyanobacterial counts."; return finalize(out)


def load_large_rivers(year: int) -> pd.DataFrame:
    if year == 2017: p = EXTERNAL / "USGS_Large_Rivers_2017_Microcystin" / "Cyanotoxins_Chl_Genetic_Data.csv"; skip = 0
    elif year == 2018: p = EXTERNAL / "USGS_Large_Rivers_2018_Microcystin" / "2018_Cyanotoxins_Chl_Genetics_Data.csv"; skip = 1
    else: p = EXTERNAL / "USGS_Large_Rivers_2019_Microcystin" / "converted" / "2019_Cyanotoxins_Chl_Genetics_Data__Cyanotoxins_Chl_Genetics_Data.csv"; skip = 2
    df = read_csv(p, skiprows=skip)
    target_c = find_col(df, ["Total microcystins plus nodularins (ug/L)"]); qual_c = find_col(df, ["Data qualifiers for Total microcystins plus nodularins"])
    out = base_frame(f"usgs_large_rivers_{year}", "total_mc_training", "external_raw", str(p), len(df)); set_common(out, df, {"site_id": ["Station ID", "USGS Station ID"], "waterbody_name": ["Station Name", "USGS Station Name"], "chla_ugL": ["Chlorophyll-a"]}); set_dates(out, series(df, ["Date", "Sample Date"])); target_from_values(out, df[target_c] if target_c else [None]*len(df), qualifiers=df[qual_c] if qual_c else None, target="total", use_half_lod=True); out["parameter_name"] = "total microcystins + nodularins"; out["notes"] = "USGS Large Rivers; nodularins are reported together with total microcystins."; return finalize(out)


def load_lake_ontario() -> pd.DataFrame:
    p = EXTERNAL / "USGS_LakeOntario_2023" / "5_Cyanotoxins.csv"; df = read_csv(p, skiprows=2); pc = find_col(df, ["Parameter_Name"]); work = df[df[pc].astype("string").str.lower().str.contains("microcystin", na=False)].copy(); out = base_frame("usgs_lake_ontario_2023", "total_mc_training", "external_raw", str(p), len(work)); set_common(out, work, {"site_id": ["Station_Number"], "waterbody_name": ["Station_Name"]}); set_dates(out, series(work, ["Sample_Datetime"])); target_from_values(out, series(work, ["Result_Value"]), qualifiers=series(work, ["Data_Qualifier_Code"]), target="total", use_half_lod=True); out["parameter_name"] = series(work, ["Parameter_Name"]); out["notes"] = "USGS Lake Ontario ELISA total microcystin + nodularins; filtered from cyanotoxin long table."; return finalize(out)


def load_se_wadeable() -> pd.DataFrame:
    p = EXTERNAL / "USGS_SE_Wadeable_Streams_2014" / "DATA TABLE 2.MICROCYSTIN AND WATER QUALITY.csv"; df = read_csv(p); out = base_frame("usgs_se_wadeable_2014", "total_mc_training", "external_raw", str(p), len(df)); set_common(out, df, {"site_id": ["NWIS Station Number"], "waterbody_name": ["Field ID"], "water_temp_c": ["Water Temperature Median (degrees Celsius)"], "ph": ["pH Median (standard units)"], "tn_mgL": ["Total Nitrogen Median (milligrams per liter)"], "tp_mgL": ["Total Phosphorus Median (milligrams per liter)"], "no3_no2_mgL": ["Dissolved Nitrate plus nitrite Median (milligrams per liter)"], "chla_ugL": ["Periphyton Chlorophyll a (micrograms per liter)"]}); target_from_values(out, series(df, ["Total Microcystin (micrograms per liter)"]), target="total", use_half_lod=True); out["notes"] = "USGS Southeast Wadeable Streams table; many covariates are site summaries rather than exact sample-time values."; return finalize(out)


def load_raritan() -> pd.DataFrame:
    p = EXTERNAL / "USGS_Raritan_River_Basin_2020_2021" / "converted" / "Table_8_Discrete_Microcystin.csv"; df = read_csv(p); out = base_frame("usgs_raritan_2020_2021", "total_mc_training", "external_raw", str(p), len(df)); set_common(out, df, {"site_id": ["Station_number"], "waterbody_name": ["Station_name"]}); set_dates(out, series(df, ["Sample_date_yyyymmdd"])); target_from_values(out, series(df, ["Total_microcystins_micrograms_per_liter"]), qualifiers=series(df, ["Total_microcystins_qualifier_codes"]), target="total", use_half_lod=False); out["notes"] = "USGS Raritan discrete microcystin; nd/bd values remain censored/missing rather than zero-imputed."; return finalize(out)


def load_simple_water(path: Path, dataset_id: str, site_candidates: Sequence[str], date_candidates: Sequence[str], target_candidates: Sequence[str], qualifier_candidates: Sequence[str] = ()) -> pd.DataFrame:
    df = read_csv(path); out = base_frame(dataset_id, "total_mc_training", "external_raw", str(path), len(df)); set_common(out, df, {"site_id": site_candidates, "waterbody_name": site_candidates}); set_dates(out, series(df, date_candidates)); target_from_values(out, series(df, target_candidates), qualifiers=series(df, qualifier_candidates) if qualifier_candidates else None, target="total", use_half_lod=True); return finalize(out)


def load_clinch() -> pd.DataFrame:
    p = EXTERNAL / "USGS_Clinch_River_Cyanotoxins" / "6_Clinch_HABs_MC_conc_water.csv"; out = load_simple_water(p, "usgs_clinch_water_2021", ["siteid"], ["datecoll"], ["mcconc"], ["qualifier"]); out["notes"] = "USGS Clinch River water MC concentration."; return out


def load_tennessee() -> pd.DataFrame:
    p = EXTERNAL / "USGS_Tennessee_Reservoirs" / "6_MidTN_HABs_MC_conc_water.csv"; out = load_simple_water(p, "usgs_tennessee_water_2022", ["siteid"], ["datecoll"], ["mcconc"], ["qualifier"]); out["notes"] = "USGS Middle Tennessee reservoir water MC concentration."; return out


def load_five_river(dataset_dir: str, dataset_id: str) -> pd.DataFrame:
    p = EXTERNAL / dataset_dir / "converted" / "CyanotoxinConc.csv"; df = read_csv(p); target = find_col(df, ["Total Microcystin (micrograms/liter)"]); qual = find_col(df, ["Total Microcystin Qualifier Codes"]); lod = find_col(df, ["Microcystin MDL", "Microcystin MRL"]); out = base_frame(dataset_id, "total_mc_training", "external_raw", str(p), len(df)); set_common(out, df, {"site_id": ["Station ID"], "waterbody_name": ["Station Name"]}); set_dates(out, series(df, ["Sample Date"])); target_from_values(out, df[target] if target else [None]*len(df), qualifiers=df[qual] if qual else None, lod_values=df[lod] if lod else None, target="total", use_half_lod=True); out["parameter_name"] = "total microcystin"; out["notes"] = "USGS cyanotoxin concentration table; converted CSV, mass concentration only."; return finalize(out)


def load_nps() -> pd.DataFrame:
    p = EXTERNAL / "USGS_National_Park_Service_Cyanotoxins" / "converted" / "Table_7_CyanoMonitoring_Results.csv"; df = read_csv(p); out = base_frame("usgs_nps_cyanomonitoring", "total_mc_training", "external_raw", str(p), len(df)); set_common(out, df, {"site_id": ["Station_name"], "waterbody_name": ["Site"], "latitude": ["Latitude"], "longitude": ["Longitude"]}); set_dates(out, series(df, ["Sample_date"])); target_from_values(out, series(df, ["Total_microcystins_plus_nodularins_in_ug_per_L"]), qualifiers=series(df, ["Data_qualifiers_for_total_microcystins_plus_nodularins"]), target="total", use_half_lod=True); out["notes"] = "USGS NPS cyanomonitoring results; total MC plus nodularins."; return finalize(out)


def load_sacramento() -> pd.DataFrame:
    p = EXTERNAL / "USGS_Sacramento_SanJoaquin_Delta" / "converted" / "CyanoWW_2025_cyanotoxins.csv"; df = read_csv(p); param = find_col(df, ["Parameter"]); work = df[df[param].astype("string").str.lower().str.contains("microcystin", na=False)].copy(); out = base_frame("usgs_sacramento_delta_2023_2025", "total_mc_training", "external_raw", str(p), len(work)); set_common(out, work, {"site_id": ["Station ID DS", "Station Abbrev. DS"], "waterbody_name": ["Station Abbrev. DS"]}); set_dates(out, series(work, ["Timestamp (PST) DS"])); target_from_values(out, series(work, ["Result Value (ug/L)"]), qualifiers=series(work, ["Result Remark"]), target="total", use_half_lod=False); out["parameter_name"] = series(work, ["Parameter"]); out["notes"] = "USGS Sacramento–San Joaquin Delta cyanotoxin results filtered to microcystin parameters."; return finalize(out)


def load_cleo() -> pd.DataFrame:
    p = path_one(RAW, "EDI569_toxins.csv"); df = read_csv(p); out = base_frame("cleo_lillinonah_risk_levels", "auxiliary_risk_class", "raw", str(p), len(df)); set_common(out, df, {"site_id": ["Site"], "waterbody_name": ["Site"]}); set_dates(out, series(df, ["Date"])); out["quality_flag"] = series(df, ["Type"]); out["total_mc_raw"] = series(df, ["toxin_level"]); out["notes"] = "Ordinal/semi-quantitative toxin level; not a concentration and not pooled with continuous MC targets."; return finalize(out)


def load_habs_predictions() -> pd.DataFrame:
    p = path_one(RAW, "HABs_预测数据.csv"); df = read_csv(p); out = base_frame("habs_nla_prediction_output", "auxiliary_prediction", "raw", str(p), len(df)); set_common(out, df, {"site_id": ["UNIQUE_ID"], "waterbody_name": ["UNIQUE_ID"], "latitude": ["latitude_epsg5072"], "longitude": ["logitude_epsg5072"]}); out["prediction_value"] = pd.to_numeric(series(df, ["cyano_log.fit"]), errors="coerce"); out["prediction_unit"] = "cyano_log.fit"; out["risk_probability"] = pd.to_numeric(series(df, ["micx_prob.fit"]), errors="coerce"); out["target_type"] = "prediction"; out["target_unit"] = "derived"; out["notes"] = "Precomputed NLA model predictions; never used as supervised labels."; return finalize(out)


def load_clear_lake_covariates() -> pd.DataFrame:
    p = EXTERNAL / "Zenodo_Clear_Lake_70yr" / "Historical_Clear_Lake_Final_Public_Database.csv"; df = read_csv(p); out = base_frame("clear_lake_70yr_covariates", "covariate_shift", "external_raw", str(p), len(df)); set_common(out, df, {"site_id": ["Station"], "waterbody_name": ["Station"], "latitude": ["Latitude"], "longitude": ["Longitude"]}); set_dates(out, series(df, ["Date"])); out["parameter_name"] = series(df, ["Renamed Parameter", "Parameter"]); out["total_mc_raw"] = series(df, ["val"]); out["target_type"] = "none"; out["notes"] = "Clear Lake long-format historical covariates (pH, DO, turbidity, suspended solids, conductivity); no microcystin target."; return finalize(out)


def load_20_reservoir_covariates() -> pd.DataFrame:
    p = EXTERNAL / "EPA_20_Reservoirs_1987_2018" / "converted" / "CyanoMaxCD_environmental_vars_FINAL__Data.csv"; df = read_csv(p); out = base_frame("epa_20_reservoirs_covariates", "covariate_shift", "external_raw", str(p), len(df)); set_common(out, df, {"site_id": ["Reservoir"], "waterbody_name": ["Reservoir"], "water_temp_c": ["julST_Celsius"], "chla_ugL": ["Chlorophyll_a_ug/l"], "tp_mgL": ["TP_ppb"], "tn_mgL": ["TKN_ppm"], "no3_no2_mgL": ["NOx_ppm"], "nh3_mgL": ["NH3_ppm"]}); set_dates(out, series(df, ["Year"])); out["target_type"] = "none"; out["parameter_name"] = "cyanobacteria/environmental model covariates"; out["notes"] = "EPA/USACE 20-reservoir environmental covariates; cyanobacterial abundance, not MC concentration."; return finalize(out)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def quality_row(dataset_id: str, task_group: str, df: pd.DataFrame, status: str) -> dict:
    target_col = "mclr_ugL" if task_group == "mc_lr_validation" else "total_mc_ugL"
    return {
        "dataset_id": dataset_id, "task_group": task_group, "status": status,
        "rows": int(len(df)), "columns": int(len(df.columns)),
        "target_measured_rows": int(df[target_col].notna().sum()) if target_col in df else 0,
        "target_model_rows": int(df[("mclr_model_ugL" if task_group == "mc_lr_validation" else "total_mc_model_ugL")].notna().sum()) if len(df) else 0,
        "censored_rows": int(df["censored_flag"].sum()) if "censored_flag" in df else 0,
        "date_rows": int(df["sample_date"].notna().sum()) if "sample_date" in df else 0,
        "coordinate_rows": int(df[["latitude", "longitude"]].notna().all(axis=1).sum()) if len(df) else 0,
        "duplicate_record_ids": int(df["record_id"].duplicated().sum()) if "record_id" in df else 0,
        "target_min": float(df[target_col].min()) if target_col in df and df[target_col].notna().any() else np.nan,
        "target_max": float(df[target_col].max()) if target_col in df and df[target_col].notna().any() else np.nan,
    }


def build_catalog(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ["standardized/total_mc", "standardized/mc_lr", "standardized/covariates", "standardized/auxiliary", "merged", "quality", "catalog"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    datasets: list[tuple[str, pd.DataFrame, str, str, bool]] = []
    # (dataset_id, frame, task_group, output_subfolder, include_in_pool)
    loaders = [
        ("lake_erie_full", load_lake_erie, "standardized/total_mc", True),
        ("lake_erie_sb_weekly", load_erie_sb_weekly, "standardized/total_mc", True),
        ("erie_esp_sensor", load_esp, "standardized/auxiliary", False),
        ("habs_nla_driver_training", load_habs_training, "standardized/total_mc", True),
        ("nla_2012_microcystin", lambda: load_nla(2012), "standardized/total_mc", True),
        ("nla_2017_microcystin", lambda: load_nla(2017), "standardized/total_mc", True),
        ("nla_2022_microcystin", lambda: load_nla(2022), "standardized/total_mc", True),
        ("ncca_2015_microcystin", lambda: load_ncca(2015), "standardized/total_mc", True),
        ("ncca_2020_microcystin", lambda: load_ncca(2020), "standardized/total_mc", True),
        ("epa_cyan_nla_modeldata", load_epacyan, "standardized/auxiliary", False),
        ("epa_wqp_microcystin", load_wqp, "standardized/total_mc", True),
        ("noaa_glerl_erie_field", read_erie_field_files, "standardized/total_mc", True),
        ("noaa_glerl_saginaw_field", read_saginaw_field_files, "standardized/total_mc", True),
        ("saginaw_bay_2008_2010", load_raw_saginaw_2008, "standardized/total_mc", True),
        ("san_francisco_estuary_cyanohab", load_san_francisco, "standardized/total_mc", True),
        ("emls_europe_mclr", load_emls, "standardized/mc_lr", True),
        ("ncei_pontchartrain_2020", load_ncei_pontchartrain, "standardized/total_mc", True),
        ("usgs_large_rivers_2017", lambda: load_large_rivers(2017), "standardized/total_mc", True),
        ("usgs_large_rivers_2018", lambda: load_large_rivers(2018), "standardized/total_mc", True),
        ("usgs_large_rivers_2019", lambda: load_large_rivers(2019), "standardized/total_mc", True),
        ("usgs_lake_ontario_2023", load_lake_ontario, "standardized/total_mc", True),
        ("usgs_se_wadeable_2014", load_se_wadeable, "standardized/total_mc", True),
        ("usgs_raritan_2020_2021", load_raritan, "standardized/total_mc", True),
        ("usgs_clinch_water_2021", load_clinch, "standardized/total_mc", True),
        ("usgs_tennessee_water_2022", load_tennessee, "standardized/total_mc", True),
        ("usgs_five_river_basins_2020", lambda: load_five_river("USGS_Five_River_Basins", "usgs_five_river_basins_2020"), "standardized/total_mc", True),
        ("usgs_north_atlantic_2020", lambda: load_five_river("USGS_North_Atlantic_Appalachian_2020", "usgs_north_atlantic_2020"), "standardized/total_mc", True),
        ("usgs_nps_cyanomonitoring", load_nps, "standardized/total_mc", True),
        ("usgs_sacramento_delta_2023_2025", load_sacramento, "standardized/total_mc", True),
        ("cleo_lillinonah_risk_levels", load_cleo, "standardized/auxiliary", False),
        ("habs_nla_prediction_output", load_habs_predictions, "standardized/auxiliary", False),
    ]

    registry_rows: list[dict] = []; quality_rows: list[dict] = []; total_pool: list[pd.DataFrame] = []; mclr_pool: list[pd.DataFrame] = []
    for dataset_id, loader, folder, include in loaders:
        try:
            df = loader()
            if df.empty:
                print("SKIP empty", dataset_id); continue
            # Ensure combined loaders have stable ids after concatenation.
            df["dataset_id"] = dataset_id
            df["record_id"] = [f"{dataset_id}:{i}" for i in range(1, len(df) + 1)]
            out_name = dataset_id + ".csv"
            write_csv(df, OUT / folder / out_name)
            task_group = str(df["task_group"].iloc[0])
            status = "included_pool" if include else "auxiliary_not_pooled"
            quality_rows.append(quality_row(dataset_id, task_group, df, status))
            registry_rows.append({"dataset_id": dataset_id, "task_group": task_group, "source_scope": df["source_scope"].iloc[0], "canonical_source_path": ";".join(sorted(set(df["source_file"].astype(str)))), "rows": len(df), "target_field": "mclr_ugL" if task_group == "mc_lr_validation" else "total_mc_ugL", "target_model_field": "mclr_model_ugL" if task_group == "mc_lr_validation" else "total_mc_model_ugL", "target_measured_rows": int(df["mclr_ugL" if task_group == "mc_lr_validation" else "total_mc_ugL"].notna().sum()), "target_model_rows": int(df["mclr_model_ugL" if task_group == "mc_lr_validation" else "total_mc_model_ugL"].notna().sum()), "include_in_merged_pool": include, "dedup_policy": "direct CSV preferred; converted duplicates skipped; cross-dataset overlap retained with provenance"})
            if include:
                if task_group == "mc_lr_validation": mclr_pool.append(df)
                elif task_group == "total_mc_training": total_pool.append(df)
        except Exception as exc:
            print("ERROR", dataset_id, repr(exc))
            registry_rows.append({"dataset_id": dataset_id, "task_group": "error", "status": "error", "error": repr(exc)})

    # French files are semicolon CSVs and have a long metadata preamble.
    try:
        france_total, france_lr = load_french()
        if not france_total.empty:
            france_total["dataset_id"] = "france_cyanotoxins_total"; france_total["record_id"] = [f"france_cyanotoxins_total:{i}" for i in range(1, len(france_total)+1)]; write_csv(france_total, OUT / "standardized/total_mc/france_cyanotoxins_total.csv"); total_pool.append(france_total); quality_rows.append(quality_row("france_cyanotoxins_total", "total_mc_training", france_total, "included_pool")); registry_rows.append({"dataset_id":"france_cyanotoxins_total","task_group":"total_mc_training","source_scope":"external_raw","canonical_source_path":"France_Cyanobacteria_Cyanotoxins_2021_2025/Extraction_cyanobacteries_2021-2025.csv","rows":len(france_total),"target_field":"total_mc_ugL","target_model_field":"total_mc_model_ugL","target_measured_rows":int(france_total.total_mc_ugL.notna().sum()),"target_model_rows":int(france_total.total_mc_model_ugL.notna().sum()),"include_in_merged_pool":True,"dedup_policy":"one preferred total parameter per site/date"})
        if not france_lr.empty:
            france_lr["dataset_id"] = "france_cyanotoxins_mclr"; france_lr["record_id"] = [f"france_cyanotoxins_mclr:{i}" for i in range(1, len(france_lr)+1)]; write_csv(france_lr, OUT / "standardized/mc_lr/france_cyanotoxins_mclr.csv"); mclr_pool.append(france_lr); quality_rows.append(quality_row("france_cyanotoxins_mclr", "mc_lr_validation", france_lr, "included_pool")); registry_rows.append({"dataset_id":"france_cyanotoxins_mclr","task_group":"mc_lr_validation","source_scope":"external_raw","canonical_source_path":"France_Cyanobacteria_Cyanotoxins_2021-2025/Extraction_cyanobacteries_*.csv","rows":len(france_lr),"target_field":"mclr_ugL","target_model_field":"mclr_model_ugL","target_measured_rows":int(france_lr.mclr_ugL.notna().sum()),"target_model_rows":int(france_lr.mclr_model_ugL.notna().sum()),"include_in_merged_pool":True,"dedup_policy":"one Microcystine-LR totale per site/date"})
    except Exception as exc:
        print("ERROR france", repr(exc)); registry_rows.append({"dataset_id":"france_cyanotoxins","task_group":"error","status":"error","error":repr(exc)})

    covariate_frames = []
    for dataset_id, loader in [("clear_lake_70yr_covariates", load_clear_lake_covariates), ("epa_20_reservoirs_covariates", load_20_reservoir_covariates)]:
        try:
            df = loader(); df["dataset_id"] = dataset_id; df["record_id"] = [f"{dataset_id}:{i}" for i in range(1,len(df)+1)]; write_csv(df, OUT / "standardized/covariates" / f"{dataset_id}.csv"); covariate_frames.append(df); quality_rows.append(quality_row(dataset_id, "covariate_shift", df, "covariate_only")); registry_rows.append({"dataset_id":dataset_id,"task_group":"covariate_shift","source_scope":"external_raw","canonical_source_path":";".join(sorted(set(df.source_file.astype(str)))),"rows":len(df),"target_field":"none","target_model_field":"none","target_measured_rows":0,"target_model_rows":0,"include_in_merged_pool":False,"dedup_policy":"long-format covariates retained per source"})
        except Exception as exc: print("ERROR covariate",dataset_id,repr(exc))

    if total_pool:
        total = pd.concat(total_pool, ignore_index=True, sort=False); total = total[CANONICAL]; write_csv(total, OUT / "merged/total_mc_training_pool.csv")
    else: total = pd.DataFrame(columns=CANONICAL)
    if mclr_pool:
        lr = pd.concat(mclr_pool, ignore_index=True, sort=False); lr = lr[CANONICAL]; write_csv(lr, OUT / "merged/mc_lr_validation_pool.csv")
    else: lr = pd.DataFrame(columns=CANONICAL)
    if covariate_frames:
        cov = pd.concat(covariate_frames, ignore_index=True, sort=False); write_csv(cov, OUT / "merged/covariate_pool.csv")
    else: cov = pd.DataFrame(columns=CANONICAL)

    registry = build_catalog(registry_rows); write_csv(registry, OUT / "catalog/dataset_registry.csv")
    quality = pd.DataFrame(quality_rows); write_csv(quality, OUT / "quality/dataset_quality.csv")
    field_catalog = pd.DataFrame([
        {"canonical_field":"total_mc_ugL","meaning":"reported measured total microcystin in ug/L; censored observations remain null","model_field":"total_mc_model_ugL","rule":"half LOD only for explicit censored result with limit"},
        {"canonical_field":"mclr_ugL","meaning":"reported measured Microcystin-LR in ug/L","model_field":"mclr_model_ugL","rule":"same censoring rule; no imputation for ordinary missing"},
        {"canonical_field":"censored_flag","meaning":"source indicates <, ND, BDL, below detection/reporting limit","model_field":"none","rule":"preserved for censored-model/sensitivity analysis"},
        {"canonical_field":"record_id","meaning":"dataset_id:source row, stable within this preparation","model_field":"none","rule":"does not assert cross-dataset identity"},
        {"canonical_field":"source_file","meaning":"relative path to original CSV under raw/external_raw","model_field":"none","rule":"provenance; converted duplicates are not selected when direct CSV exists"},
    ]); write_csv(field_catalog, OUT / "catalog/field_catalog.csv")

    # CSV-only inventory note: useful downloaded objects without CSV are listed
    # explicitly so they are not mistaken for absent downloads.
    excluded = pd.DataFrame([
        {"dataset_id":"NESDC_Donghu_2002_2006","reason":"downloaded but source data available only as XLS; CSV-only constraint","action":"not processed; convert to CSV later"},
        {"dataset_id":"NESDC_Donghu_2002_2006_Biology","reason":"downloaded but source data available only as XLS","action":"not processed; convert to CSV later"},
        {"dataset_id":"NESDC_Donghu_2005_2006_Meteorology","reason":"downloaded but source data available only as XLS","action":"not processed; convert to CSV later"},
        {"dataset_id":"Alberta_Cyanobacteria_Bloom_Surveillance","reason":"no CSV present in external_raw","action":"check download status report; keep raw archive"},
        {"dataset_id":"Dryad_Uruguay_Rio_de_la_Plata","reason":"no CSV present in external_raw","action":"check download status report; keep raw archive"},
        {"dataset_id":"USDA_Georgia_Farm_Ponds","reason":"no CSV present in external_raw","action":"check download status report; keep raw archive"},
        {"dataset_id":"HABs_预测数据","reason":"prediction output rather than observed label","action":"stored under standardized/auxiliary; never merge into supervised pool"},
        {"dataset_id":"EPA_WQP_converted_result","reason":"duplicate of extracted/result.csv","action":"not merged; direct CSV selected"},
        {"dataset_id":"NOAA_GLERL_Erie_converted_copies","reason":"converted duplicates of direct field CSVs","action":"not merged; direct CSV selected"},
    ]); write_csv(excluded, OUT / "catalog/excluded_or_unprocessed.csv")

    summary = {"script":"model_redo/scripts/prepare_data_processed.py", "raw_root":str(RAW), "external_root":str(EXTERNAL), "output_root":str(OUT), "csv_only":True, "raw_files_untouched":True, "total_pool_rows":int(len(total)), "total_pool_model_rows":int(total.total_mc_model_ugL.notna().sum()) if len(total) else 0, "mclr_pool_rows":int(len(lr)), "mclr_pool_model_rows":int(lr.mclr_model_ugL.notna().sum()) if len(lr) else 0, "covariate_pool_rows":int(len(cov)), "dataset_count":int(len(registry_rows)), "error_count":int((registry.get('task_group',pd.Series(dtype=str))=='error').sum()) if len(registry) else 0}
    (OUT / "catalog/processing_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
