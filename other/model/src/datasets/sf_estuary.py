import pandas as pd

from src.clean import (
    clip_outliers_iqr,
    drop_high_missing_columns,
    fix_negative_values,
    generate_quality_report,
    load_csv_safe,
    remove_quality_control_rows,
    save_cleaned,
    unify_site_codes,
)
from src.config import get_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_configs()["sf_estuary"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path, encoding=cfg.encoding)

    df = remove_quality_control_rows(df, column="DWR_Site", sentinel="FieldCont")
    df = remove_quality_control_rows(df, column="EMP_Site", sentinel="FieldCont")

    df = unify_site_codes(df, site_col_a="DWR_Site", site_col_b="EMP_Site")

    df = fix_negative_values(df, columns=cfg.negative_to_nan_cols)

    df = drop_high_missing_columns(df, columns=cfg.columns_to_drop)

    df = clip_outliers_iqr(df, column="dwr.MIC_totbvL", factor=3.0)

    df["Collection_Date"] = pd.to_datetime(df["Collection_Date"], errors="coerce")
    df = df.sort_values("Collection_Date").reset_index(drop=True)

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
