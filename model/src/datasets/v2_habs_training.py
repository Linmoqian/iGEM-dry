import pandas as pd

from src.clean import (
    clip_outliers_iqr,
    generate_quality_report,
    load_csv_safe,
    save_cleaned,
)
from src.config import get_v2_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_v2_configs()["habs_training"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path)

    # P_Legacy_P 极端负值标记
    df = clip_outliers_iqr(df, column="P_Legacy_P", factor=3.0)

    # 解析日期
    if "DATE_COL" in df.columns:
        df["DATE_COL"] = pd.to_datetime(
            df["DATE_COL"], format="mixed", errors="coerce"
        )

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
