"""特征工程模块：列选择、时间特征提取、分类编码、目标变量处理。"""

import re

import numpy as np
import pandas as pd

from src.config import (
    AGG_INPUT_COLS,
    CATEGORICAL_COLS,
    CLEANED_DIR,
    CLIMATE_COLS,
    DATASET_REGISTRY,
    DROP_COLS,
    LAND_USE_COLS,
    LOCATION_COLS,
    N_BUDGET_COLS,
    P_BUDGET_COLS,
    TARGET_COLS,
    TERRAIN_COLS,
    WATER_QUALITY_COLS,
)
from src.logger import log_info, log_success, log_warning

FEATURE_COLS = (
    WATER_QUALITY_COLS
    + CLIMATE_COLS
    + LAND_USE_COLS
    + TERRAIN_COLS
    + N_BUDGET_COLS
    + P_BUDGET_COLS
    + AGG_INPUT_COLS
    + LOCATION_COLS
)


def _add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """从 DATE_COL 提取月份并做 sin/cos 周期编码。"""
    df = df.copy()
    if "DATE_COL" not in df.columns:
        return df
    months = df["DATE_COL"].dt.month
    df["MONTH_sin"] = np.sin(2 * np.pi * months / 12)
    df["MONTH_cos"] = np.cos(2 * np.pi * months / 12)
    return df


def _encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """对分类变量做 one-hot 编码，P_Legacy_P_outlier 转 int。"""
    df = df.copy()
    if "P_Legacy_P_outlier" in df.columns:
        df["P_Legacy_P_outlier"] = df["P_Legacy_P_outlier"].astype(int)
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, dtype=int)
            df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
    return df


def build_feature_matrix(
    df: pd.DataFrame,
    task: str = "classification",
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """构建特征矩阵和目标变量。

    Parameters
    ----------
    df : 原始清洗后 DataFrame (来自 v2_habs_training_cleaned.parquet)
    task : "classification" 使用 MICX_DET，"regression" 使用 log10(MICX)

    Returns
    -------
    X : 特征 DataFrame (NaN 保留，树模型原生处理)
    y : 目标 Series
    feature_names : 特征列名列表
    """
    log_info(f"构建特征矩阵 (task={task}): {len(df)} 行")

    # 时间特征（在丢弃 DATE_COL 之前提取）
    df = _add_temporal_features(df)

    # 目标变量
    if task == "classification":
        target_col = "MICX_DET"
        valid = df[target_col].notna()
        y = df.loc[valid, target_col].astype(int)
    elif task == "regression":
        target_col = "MICX"
        valid = df[target_col].notna() & (df[target_col] > 0)
        y = np.log10(df.loc[valid, target_col])
    else:
        msg = f"未知任务类型: {task}"
        raise ValueError(msg)

    df_valid = df.loc[valid].copy()
    n_dropped = len(df) - len(df_valid)
    if n_dropped > 0:
        log_info(f"移除 {n_dropped} 条目标缺失行，剩余 {len(df_valid)} 行")

    # 分类编码
    df_valid = _encode_categoricals(df_valid)

    # 丢弃元数据和目标列
    cols_to_remove = set(DROP_COLS) | set(TARGET_COLS)
    # 移除原始 N/P 预算列中未被选为代表列的（避免冗余）
    all_n_budget = [
        c for c in df_valid.columns
        if c.startswith("N_") and c not in N_BUDGET_COLS
    ]
    all_p_budget = [
        c for c in df_valid.columns
        if c.startswith("P_") and c not in P_BUDGET_COLS and c != "P_Legacy_P_outlier"
    ]
    cols_to_remove.update(all_n_budget)
    cols_to_remove.update(all_p_budget)

    # 保留 AG_ECO9_NM 编码列（如果有），否则丢弃原始列
    if "AG_ECO9_NM" in df_valid.columns:
        cols_to_remove.add("AG_ECO9_NM")

    # KffactWs 与 AgKffactWs 高度相关
    if "KffactWs" in df_valid.columns:
        cols_to_remove.add("KffactWs")

    # wet_ws 与其他土地利用列共线性
    if "wet_ws" in df_valid.columns:
        cols_to_remove.add("wet_ws")

    existing_to_remove = [c for c in cols_to_remove if c in df_valid.columns]
    df_valid = df_valid.drop(columns=existing_to_remove)

    # 特征列 = 预定义 + 衍生 + one-hot
    base_features = [c for c in FEATURE_COLS if c in df_valid.columns]
    derived = ["MONTH_sin", "MONTH_cos", "P_Legacy_P_outlier"]
    derived = [c for c in derived if c in df_valid.columns]
    one_hot_cols = [
        c for c in df_valid.columns
        if any(c.startswith(f"{cat}_") for cat in CATEGORICAL_COLS)
    ]
    feature_names = base_features + derived + one_hot_cols
    # 去重保序
    seen: set[str] = set()
    unique_features: list[str] = []
    for f in feature_names:
        if f not in seen and f in df_valid.columns:
            seen.add(f)
            unique_features.append(f)
    feature_names = unique_features

    X = df_valid[feature_names].copy()

    # 特征缺失率报告
    missing_pct = X.isnull().mean() * 100
    high_missing = missing_pct[missing_pct > 10]
    if not high_missing.empty:
        for col, pct in high_missing.items():
            log_warning(f"{col}: {pct:.1f}% 缺失")

    log_success(
        f"特征矩阵: {X.shape[0]} 行 × {X.shape[1]} 列, "
        f"目标分布: {y.describe().to_dict()}"
    )
    return X, y, feature_names


# ---------------------------------------------------------------------------
# 多数据集支持
# ---------------------------------------------------------------------------

def _parse_detection_limits(series: pd.Series) -> pd.Series:
    """将 '< X' / '<X' 检测限标记替换为 X/2，然后转 float。"""
    s = series.astype(str).str.strip()
    mask_lt = s.str.contains("<", na=False, regex=False)
    if mask_lt.any():
        numeric_part = s[mask_lt].str.replace("<", "", regex=False).str.strip()
        half_vals = pd.to_numeric(numeric_part, errors="coerce") / 2
        s = s.copy()
        s[mask_lt] = half_vals.astype(str)
    return pd.to_numeric(s, errors="coerce")


def _build_lake_erie(
    df: pd.DataFrame, task: str,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Lake Erie 特征构建。"""
    mc_col = "Total Microcystins (\u00b5g/L)"
    date_col = "Date"

    # 预处理 MC 列（检测限）
    df = df.copy()
    df[mc_col] = _parse_detection_limits(df[mc_col])

    # Secchi: 非数值 → NaN
    if "Secchi (m)" in df.columns:
        df["Secchi (m)"] = pd.to_numeric(df["Secchi (m)"], errors="coerce")

    # TN:TP: #DIV/0! → NaN
    if "TN:TP (molar)" in df.columns:
        df["TN:TP (molar)"] = pd.to_numeric(df["TN:TP (molar)"], errors="coerce")

    # Chlorophyll 负值 → 0
    chla_col = "Chlorophyll (\u00b5g/L)"
    if chla_col in df.columns:
        df[chla_col] = df[chla_col].clip(lower=0)

    # 时间特征
    if date_col in df.columns:
        months = pd.to_datetime(df[date_col], errors="coerce").dt.month
        df["MONTH_sin"] = np.sin(2 * np.pi * months / 12)
        df["MONTH_cos"] = np.cos(2 * np.pi * months / 12)

    # 目标变量
    threshold = 0.15
    valid = df[mc_col].notna()
    if task == "classification":
        y = (df.loc[valid, mc_col] > threshold).astype(int)
    else:
        positive = valid & (df[mc_col] > 0)
        y = np.log10(df.loc[positive, mc_col])
        valid = positive

    df_valid = df.loc[valid].copy()
    log_info(f"移除 {len(df) - len(df_valid)} 条无效行，剩余 {len(df_valid)} 行")

    # 特征列选择
    erie_features = [
        "Depth (m)", "Secchi (m)", "Water Temp at 1 meter (C)",
        "Chlorophyll (\u00b5g/L)",
        "Nitrate+NO2 (\u00b5mol/L)", "Ammonium (\u00b5mol/L)",
        "Nitrite (\u00b5mol/L)", "DRP (\u00b5mol/L)", "Silicate (\u00b5mol/L)",
        "Nitrate (\u00b5mol/L)", "TP (\u00b5mol/L)", "TKN (\u00b5mol/L)",
        "TN (\u00b5mol/L)", "TN:TP (molar)",
        "Green algae-chla \u00b5g/l", "Bluegreen algae-chla \u00b5g/l",
        "Diatoms-chla \u00b5g/l", "Cryptophytes-chla \u00b5g/l",
        "Yellow substances \u00b5g/l",
        "Lat", "Long",
        "MONTH_sin", "MONTH_cos",
    ]
    feature_names = [c for c in erie_features if c in df_valid.columns]
    X = df_valid[feature_names].copy()

    _report_missing(X)
    X, feature_names = _sanitize_feature_names(X, feature_names)
    log_success(f"Lake Erie 特征矩阵: {X.shape[0]} 行 × {X.shape[1]} 列")
    return X, y, feature_names


def _build_sf_estuary(
    df: pd.DataFrame, task: str,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """SF Estuary 特征构建。"""
    mc_col = "ucd.ppia.MC.total.ugL"
    date_col = "Collection_Date"

    df = df.copy()

    # 时间特征
    if date_col in df.columns:
        months = pd.to_datetime(df[date_col], errors="coerce").dt.month
        df["MONTH_sin"] = np.sin(2 * np.pi * months / 12)
        df["MONTH_cos"] = np.cos(2 * np.pi * months / 12)

    # 目标变量
    valid = df[mc_col].notna()
    if task == "classification":
        y = (df.loc[valid, mc_col] > 0).astype(int)
    else:
        positive = valid & (df[mc_col] > 0)
        y = np.log10(df.loc[positive, mc_col])
        valid = positive

    df_valid = df.loc[valid].copy()
    log_info(f"移除 {len(df) - len(df_valid)} 条无效行，剩余 {len(df_valid)} 行")

    # 特征列选择（排除 >45% 缺失和标识符）
    sf_features = [
        "field.Water.temp", "field.DO.mgL", "field.SC.uScm",
        "field.Salinity", "field.NTU", "field.pH",
        "bryte.NH4.mgL", "bryte.NO3.mgL", "bryte.Chloride.mgL",
        "bryte.DOC.mgL", "bryte.TOC.mgL", "bryte.DON.mgL",
        "bryte.SRP.mgL", "bryte.TP.mgL", "bryte.SiO2.mgL",
        "bryte.VSS.mgL", "bryte.TDS.mgL", "bryte.TSS.mgL",
        "bryte.amb.Chla.ugL", "bryte.amb.Pheo.ugL",
        "ucd.qpcr.total.MIC",
        "Lat", "Lon",
        "MONTH_sin", "MONTH_cos",
    ]
    feature_names = [c for c in sf_features if c in df_valid.columns]
    X = df_valid[feature_names].copy()

    _report_missing(X)
    X, feature_names = _sanitize_feature_names(X, feature_names)
    log_success(f"SF Estuary 特征矩阵: {X.shape[0]} 行 × {X.shape[1]} 列")
    return X, y, feature_names


def _report_missing(X: pd.DataFrame) -> None:
    """报告高缺失率特征。"""
    missing_pct = X.isnull().mean() * 100
    high_missing = missing_pct[missing_pct > 10]
    if not high_missing.empty:
        for col, pct in high_missing.items():
            log_warning(f"{col}: {pct:.1f}% 缺失")


def _sanitize_feature_names(
    X: pd.DataFrame, feature_names: list[str],
) -> tuple[pd.DataFrame, list[str]]:
    """清洗特征列名，移除 LightGBM 不支持的特殊字符。"""
    rename_map = {}
    for col in X.columns:
        clean = col.replace("\u00b5", "u")  # µ → u
        clean = re.sub(r"[^a-zA-Z0-9_.]", "_", clean)
        clean = re.sub(r"_+", "_", clean).strip("_")
        if not clean:
            clean = "feature"
        rename_map[col] = clean
    X = X.rename(columns=rename_map)
    feature_names = [rename_map.get(c, c) for c in feature_names]
    return X, feature_names


def build_feature_matrix_for(
    df: pd.DataFrame,
    dataset: str,
    task: str = "classification",
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """按数据集名称构建特征矩阵。

    Parameters
    ----------
    df : 清洗后 DataFrame
    dataset : 数据集名称 (habs_training / lake_erie / sf_estuary)
    task : classification 或 regression

    Returns
    -------
    X, y, feature_names
    """
    if dataset == "habs_training":
        return build_feature_matrix(df, task=task)
    if dataset == "lake_erie":
        return _build_lake_erie(df, task=task)
    if dataset == "sf_estuary":
        return _build_sf_estuary(df, task=task)
    msg = f"未知数据集: {dataset}，可选: {list(DATASET_REGISTRY.keys())}"
    raise ValueError(msg)
