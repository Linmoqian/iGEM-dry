"""统一清洗流水线 — 将原始数据转换为标准格式建模表。"""

import json
import sys
import io
from pathlib import Path

import pandas as pd

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
DOCS_DIR = BASE_DIR / "data" / "docs"

# Unit conversion constants
TN_UMOL_TO_MG = 0.014  # µmol/L → mg/L (as N)
TP_UMOL_TO_MG = 0.031  # µmol/L → mg/L (as P)
CHLA_MG_TO_UG = 1000   # mg/L → µg/L


def clean_lake_erie() -> dict:
    """清洗 Lake Erie 全湖采样数据。"""
    print("[Lake Erie] 开始清洗...")
    path = RAW_DIR / "数据汇总v2(clf)" / "1.数据汇总" / "01_Lake_Erie_采样" / "Lake_Erie_全湖采样数据_2013-2025.csv"
    df = pd.read_csv(path, encoding="latin1")
    n_input = len(df)
    print(f"  输入: {n_input} 行, {len(df.columns)} 列")

    # Drop empty columns
    drop_cols = [c for c in df.columns if c.startswith("Unnamed") or c == "Light attenuation coefficient /m"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Handle MC detection limits
    mc_col = "Total Microcystins (µg/L)"
    if mc_col in df.columns:
        lt_mask = df[mc_col].astype(str).str.contains("<", na=False)
        n_lt = lt_mask.sum()
        df.loc[lt_mask, mc_col] = 0.075  # half of 0.15 LOD
        df[mc_col] = pd.to_numeric(df[mc_col], errors="coerce")
        print(f"  MC 检测限处理: {n_lt} 条 <0.15 → 0.075")

    # Unit conversions
    for col, factor, new_name in [
        ("TN (µmol/L)", TN_UMOL_TO_MG, "tn_mgL"),
        ("TP (µmol/L)", TP_UMOL_TO_MG, "tp_mgL"),
        ("Ammonium (µmol/L)", TN_UMOL_TO_MG, "nh3_mgL"),
        ("Nitrate+NO2 (µmol/L)", TN_UMOL_TO_MG, "no3_no2_mgL"),
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[new_name] = df[col] * factor
            print(f"  单位转换: {col} × {factor} → {new_name}")

    # Chlorophyll clip negative
    chla_col = "Chlorophyll (µg/L)"
    if chla_col in df.columns:
        df[chla_col] = pd.to_numeric(df[chla_col], errors="coerce").clip(lower=0)

    # Parse dates
    if "Date" in df.columns:
        df["sample_date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["year"] = df["sample_date"].dt.year
        df["month"] = df["sample_date"].dt.month
        import numpy as np
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # Rename to standard fields
    rename_map = {
        mc_col: "total_mc_ugL",
        "Chlorophyll (µg/L)": "chla_ugL",
        "Water Temp at 1 meter (C)": "water_temp_c",
        "Secchi (m)": "secchi_m",
        "Depth (m)": "max_depth_m",
        "Lat": "latitude",
        "Long": "longitude",
        "Site name": "site_id",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["data_source"] = "erie"

    # Save
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CLEANED_DIR / "erie_clean.pkl"
    df.to_pickle(out_path)

    report = {
        "dataset": "lake_erie",
        "n_input": n_input,
        "n_output": len(df),
        "n_cols": len(df.columns),
        "target_missing_pct": round(df["total_mc_ugL"].isna().mean() * 100, 1) if "total_mc_ugL" in df.columns else None,
        "target_stats": df["total_mc_ugL"].describe().to_dict() if "total_mc_ugL" in df.columns else None,
    }
    print(f"  输出: {len(df)} 行 → {out_path}")
    return report


def clean_habs_training() -> dict:
    """清洗 HABs 模型训练数据。"""
    print("[HABs Training] 开始清洗...")
    path = RAW_DIR / "数据汇总v2(clf)" / "1.数据汇总" / "02_HABs_驱动因子模型" / "HABs_模型训练数据.csv"
    df = pd.read_csv(path)
    n_input = len(df)
    print(f"  输入: {n_input} 行, {len(df.columns)} 列")

    # Parse dates
    if "DATE_COL" in df.columns:
        df["sample_date"] = pd.to_datetime(df["DATE_COL"], format="mixed", errors="coerce")
        df["year"] = df["sample_date"].dt.year
        df["month"] = df["sample_date"].dt.month
        import numpy as np
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # Chla unit conversion: mg/L → µg/L
    if "CHLA_RESULT" in df.columns:
        df["chla_ugL"] = pd.to_numeric(df["CHLA_RESULT"], errors="coerce") * CHLA_MG_TO_UG
        print(f"  Chla: mg/L × {CHLA_MG_TO_UG} → µg/L")

    # Rename
    rename_map = {
        "MICX": "total_mc_ugL",
        "MICX_DET": "mc_detected",
        "TEMPERATURE": "water_temp_c",
        "PH": "ph",
        "DO_SURF": "do_mgL",
        "TURB": "turbidity_ntu",
        "NTL": "tn_mgL",
        "PTL": "tp_mgL",
        "MAXDEPTH": "max_depth_m",
        "LAT_DD83": "latitude",
        "LON_DD83": "longitude",
        "SITE_ID": "site_id",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["data_source"] = "habs_nla"

    out_path = CLEANED_DIR / "habs_nla_clean.pkl"
    df.to_pickle(out_path)

    report = {
        "dataset": "habs_training",
        "n_input": n_input,
        "n_output": len(df),
        "n_cols": len(df.columns),
        "target_missing_pct": round(df["total_mc_ugL"].isna().mean() * 100, 1) if "total_mc_ugL" in df.columns else None,
        "target_stats": df["total_mc_ugL"].describe().to_dict() if "total_mc_ugL" in df.columns else None,
    }
    print(f"  输出: {len(df)} 行 → {out_path}")
    return report


def clean_emls() -> dict:
    """清洗 EMLS Europe 数据。"""
    print("[EMLS Europe] 开始清洗...")
    path = RAW_DIR / "1.测试数据-第一版本" / "欧洲地区性数据" / "edi.176.5" / "EMLSdata_10Aug_afterRev_dateformated.csv"
    df = pd.read_csv(path, encoding="utf-8-sig")
    n_input = len(df)
    print(f"  输入: {n_input} 行, {len(df.columns)} 列")

    # Country corrections
    if "Country" in df.columns:
        df["Country"] = df["Country"].replace({"FR": "France", "Lithouania": "Lithuania"})

    # Parse dates
    if "Date" in df.columns:
        df["sample_date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["year"] = df["sample_date"].dt.year
        df["month"] = df["sample_date"].dt.month
        import numpy as np
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # MC-LR zero value handling
    mclr_col = "MC_LR_ugL"
    if mclr_col in df.columns:
        n_zero = (df[mclr_col] == 0).sum()
        n_total = len(df)
        print(f"  MC-LR 零值: {n_zero}/{n_total} ({n_zero*100/n_total:.1f}%)")
        # Keep as-is; sensitivity analysis will handle 0 vs LOD/2 vs LOD

    # Rename
    rename_map = {
        "MC_LR_ugL": "mclr_ugL",
        "SurfaceTemperature_C": "water_temp_c",
        "TP_mgL": "tp_mgL",
        "TN_mgL": "tn_mgL",
        "NO3NO2_mgL": "no3_no2_mgL",
        "NH3_mgL": "nh3_mgL",
        "PO4_ugL": "po4_ugL",
        "Chlorophylla_ugL": "chla_ugL",
        "SecchiDepth_m": "secchi_m",
        "MaximumDepth_m": "max_depth_m",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Lake_ID": "site_id",
        "LakeName": "waterbody_name",
        "Country": "country",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["data_source"] = "emls"

    # Also create total_mc from sum of MC variants
    mc_variant_cols = ["MC_YR_ugL", "MC_dmRR_ugL", "MC_RR_ugL", "MC_dmLR_ugL",
                       "MC_LY_ugL", "MC_LW_ugL", "MC_LF_ugL"]
    available_variants = [c for c in mc_variant_cols if c in df.columns]
    if available_variants:
        df["total_mc_ugL"] = df[available_variants].apply(pd.to_numeric, errors="coerce").sum(axis=1)
        print(f"  总 MC = MC变体之和: {len(available_variants)} 个变体")

    out_path = CLEANED_DIR / "emls_clean.pkl"
    df.to_pickle(out_path)

    report = {
        "dataset": "emls_europe",
        "n_input": n_input,
        "n_output": len(df),
        "n_cols": len(df.columns),
        "mclr_zero_pct": round((df["mclr_ugL"] == 0).mean() * 100, 1) if "mclr_ugL" in df.columns else None,
        "mclr_stats": df["mclr_ugL"].describe().to_dict() if "mclr_ugL" in df.columns else None,
    }
    print(f"  输出: {len(df)} 行 → {out_path}")
    return report


def clean_ncca2015() -> dict:
    """清洗 EPA NCCA 2015 Great Lakes LC/MS/MS 数据。"""
    print("[EPA NCCA 2015] 开始清洗...")
    path = BASE_DIR / "data" / "external_raw" / "EPA_NCCA_2015_GreatLakes" / "NCCA_2015_Great_Lakes_LCMSMS_Data.xlsx"
    if not path.exists():
        print(f"  跳过: 文件不存在 {path}")
        return {"dataset": "ncca2015", "error": "file not found"}

    df = pd.read_excel(path)
    n_input = len(df)
    print(f"  输入: {n_input} 行, {len(df.columns)} 列")

    # MC-LR: 0.10 is the LOD
    mclr_col = "MCLR_(µg/L)"
    if mclr_col in df.columns:
        df[mclr_col] = pd.to_numeric(df[mclr_col], errors="coerce")
        n_lod = (df[mclr_col] == 0.10).sum()
        print(f"  MC-LR LOD (0.10): {n_lod}/{n_input} ({n_lod*100/n_input:.1f}%)")

    # Parse dates
    date_col = "COL_DATE_(YYYYMMDD)"
    if date_col in df.columns:
        df["sample_date"] = pd.to_datetime(df[date_col].astype(str), format="%Y%m%d", errors="coerce")
        df["year"] = df["sample_date"].dt.year
        df["month"] = df["sample_date"].dt.month
        import numpy as np
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # Rename
    rename_map = {
        mclr_col: "mclr_ugL",
        "LAT_DD84": "latitude",
        "LON_DD84": "longitude",
        "SITE_ID": "site_id",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["data_source"] = "ncca2015"

    # Total MC from sum of all MC variants
    all_mc_cols = [c for c in df.columns if "MCL" in c and "µg/L" in c]
    if all_mc_cols:
        df["total_mc_ugL"] = df[all_mc_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)

    out_path = CLEANED_DIR / "ncca2015_clean.pkl"
    df.to_pickle(out_path)

    report = {
        "dataset": "ncca2015",
        "n_input": n_input,
        "n_output": len(df),
        "n_cols": len(df.columns),
        "mclr_lod_pct": round((df["mclr_ugL"] == 0.10).mean() * 100, 1) if "mclr_ugL" in df.columns else None,
        "mclr_stats": df["mclr_ugL"].describe().to_dict() if "mclr_ugL" in df.columns else None,
    }
    print(f"  输出: {len(df)} 行 → {out_path}")
    return report


def main():
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    reports = {}

    for name, fn in [
        ("lake_erie", clean_lake_erie),
        ("habs_training", clean_habs_training),
        ("emls", clean_emls),
        ("ncca2015", clean_ncca2015),
    ]:
        try:
            reports[name] = fn()
        except Exception as e:
            print(f"[{name}] 错误: {e}")
            reports[name] = {"error": str(e)}

    # Save reports
    report_path = CLEANED_DIR / "cleaning_reports.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n清洗报告已保存: {report_path}")

    # Summary
    print("\n=== 清洗完成 ===")
    for name, r in reports.items():
        if "error" in r:
            print(f"  {name}: 错误 - {r['error']}")
        else:
            print(f"  {name}: {r.get('n_input','?')} → {r.get('n_output','?')} 行")


if __name__ == "__main__":
    main()
