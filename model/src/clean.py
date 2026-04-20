import json
import re
from io import StringIO
from pathlib import Path

import pandas as pd

from src.config import CLEANED_DIR
from src.logger import log_error, log_info, log_success, log_warning


def load_csv_safe(
    filepath: Path,
    encoding: str = "utf-8-sig",
    comment: str | None = None,
    skiprows: int = 0,
) -> pd.DataFrame:
    log_info(f"读取文件: {filepath.name}")
    try:
        df = pd.read_csv(
            filepath,
            encoding=encoding,
            comment=comment,
            skiprows=skiprows,
            na_values=["", "NA", "N/A", "nd"],
        )
        log_success(f"读取完成: {len(df)} 行, {len(df.columns)} 列")
        return df
    except Exception as e:
        log_error(f"读取失败: {e}")
        raise


def remove_quality_control_rows(df: pd.DataFrame, column: str, sentinel: str) -> pd.DataFrame:
    mask = df[column].astype(str).str.strip() == sentinel
    n_removed = mask.sum()
    if n_removed > 0:
        df = df[~mask].reset_index(drop=True)
        log_info(f"移除 {n_removed} 条质控行 (sentinel='{sentinel}')")
    return df


def fix_negative_values(df: pd.DataFrame, columns: list[str], replace_with: float = float("nan")) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            numeric = pd.to_numeric(df[col], errors="coerce")
            mask = numeric < 0
            n_neg = mask.sum()
            if n_neg > 0:
                df = df.copy()
                df.loc[mask, col] = replace_with
                log_warning(f"{col}: {n_neg} 条负值已替换为 NaN")
    return df


def fix_country_names(df: pd.DataFrame, corrections: dict[str, str], column: str = "Country") -> pd.DataFrame:
    if column in df.columns and corrections:
        for wrong, correct in corrections.items():
            mask = df[column] == wrong
            n = mask.sum()
            if n > 0:
                df = df.copy()
                df.loc[mask, column] = correct
                log_info(f"国家名修正: '{wrong}' -> '{correct}' ({n} 条)")
    return df


def drop_high_missing_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    existing = [c for c in columns if c in df.columns]
    if existing:
        df = df.drop(columns=existing)
        log_info(f"已删除 {len(existing)} 个高缺失列")
    return df


def unify_site_codes(df: pd.DataFrame, site_col_a: str, site_col_b: str, output_col: str = "Site") -> pd.DataFrame:
    df = df.copy()
    df[output_col] = df[site_col_a].fillna(df[site_col_b])
    log_info(f"站点编码已统一至列 '{output_col}'")
    return df


def clip_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 3.0) -> pd.DataFrame:
    if column not in df.columns:
        return df
    series = pd.to_numeric(df[column], errors="coerce")
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    upper = q3 + factor * iqr
    flag_col = f"{column}_outlier"
    df = df.copy()
    df[flag_col] = series > upper
    n_outliers = df[flag_col].sum()
    if n_outliers > 0:
        log_warning(f"{column}: {n_outliers} 个极端值已标记 (>{upper:.2f})")
    return df


def generate_quality_report(df: pd.DataFrame, dataset_name: str) -> dict:
    return {
        "dataset": dataset_name,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_pct": {
            col: round(pct, 2)
            for col, pct in (df.isnull().mean() * 100).items()
            if pct > 0
        },
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def save_cleaned(df: pd.DataFrame, name: str, report: dict | None = None) -> Path:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = CLEANED_DIR / f"{name}.parquet"
    df.to_parquet(output_path, index=False, engine="pyarrow")
    log_success(f"已保存: {output_path} ({len(df)} 行)")
    if report:
        report_path = CLEANED_DIR / f"{name}_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    return output_path


def replace_detection_limits(
    df: pd.DataFrame,
    column: str,
    strategy: str = "half",
) -> pd.DataFrame:
    """将检测限标记替换为数值。

    处理的标记: '< 0.15', '<0.15', 'bdl', 'bd', 'bdll',
    'below detection', 'below dectection', 'nd', 'ND', 'ns', 'NS',
    '<LLOD', 'nq', 'positive, nq'

    strategy='half': 对 '<X' 类标记用 X/2 替换，其他标记用 NaN
    strategy='nan': 全部替换为 NaN
    """
    if column not in df.columns:
        return df

    df = df.copy()
    series = df[column].astype(str).str.strip()
    is_na = df[column].isna()

    text_markers = {
        "bdl", "bd", "bdll", "below detection", "below dectection",
        "nd", "ns", "nq", "positive, nq", "<llod",
    }
    lower = series.str.lower().str.strip()

    marker_mask = lower.isin(text_markers) & ~is_na
    n_markers = marker_mask.sum()
    df.loc[marker_mask, column] = float("nan")

    less_than_mask = series.str.match(r"^<\s*\d+\.?\d*$") & ~is_na
    n_less_than = less_than_mask.sum()
    if n_less_than > 0:
        limit_values = series[less_than_mask].str.extract(
            r"^<\s*(\d+\.?\d*)$", expand=False,
        ).astype(float)
        df.loc[less_than_mask, column] = (
            limit_values / 2 if strategy == "half" else float("nan")
        )

    df[column] = pd.to_numeric(df[column], errors="coerce")
    total = n_markers + n_less_than
    if total > 0:
        log_info(f"{column}: {total} 条检测限标记已处理 (strategy={strategy})")
    return df


def replace_sentinel_values(
    df: pd.DataFrame,
    columns: list[str],
    sentinel: float = -1000,
    replace_with: float = float("nan"),
) -> pd.DataFrame:
    """将指定列中的哨兵值替换为 NaN。"""
    df = df.copy()
    total = 0
    for col in columns:
        if col not in df.columns:
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        mask = numeric == sentinel
        n = mask.sum()
        if n > 0:
            df.loc[mask, col] = replace_with
            total += n
    if total > 0:
        log_info(f"哨兵值 {sentinel}: {total} 处已替换为 NaN")
    return df


def parse_multirow_header_csv(
    filepath: Path,
    header_rows: int = 7,
    encoding: str = "latin1",
) -> pd.DataFrame:
    """读取多行表头 CSV，合并为一个有效列名行。"""
    log_info(f"解析多行表头: {filepath.name} (前 {header_rows} 行)")

    # 读取原始行
    with open(filepath, encoding=encoding, errors="replace") as f:
        lines = [line.rstrip("\n").rstrip("\r") for line in f.readlines()]

    # 解析多行表头
    header_lines = lines[:header_rows]
    sep_counts = [line.count(",") for line in header_lines]
    n_cols = max(sep_counts) + 1

    merged_names: list[str] = []
    for col_idx in range(n_cols):
        parts = []
        for line in header_lines:
            fields = line.split(",")
            if col_idx < len(fields):
                val = fields[col_idx].strip().strip('"')
                if val and not val.startswith("Unnamed") and val != "#":
                    parts.append(val)
        merged_names.append(" - ".join(parts) if parts else f"col_{col_idx}")

    # 清理列名：去除特殊字符
    cleaned_names: list[str] = []
    for name in merged_names:
        name = re.sub(r"\s+", " ", name).strip()
        name = name.replace("(", "").replace(")", "")
        cleaned_names.append(name)

    # 读取数据部分
    data_text = "\n".join(lines[header_rows:])
    df = pd.read_csv(
        StringIO(data_text),
        header=None,
        names=cleaned_names[:n_cols],
        na_values=["", "NA", "N/A", "nd", "ns", "bdl", "bd"],
    )

    log_success(f"解析完成: {len(df)} 行, {len(df.columns)} 列")
    return df
