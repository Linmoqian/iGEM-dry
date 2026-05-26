import pandas as pd

from src.clean import (
    clip_outliers_iqr,
    fix_country_names,
    generate_quality_report,
    load_csv_safe,
    save_cleaned,
)
from src.config import get_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_configs()["emls_europe"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path)

    df = fix_country_names(df, corrections=cfg.country_corrections)

    df = clip_outliers_iqr(df, column="Chlorophylla_ugL", factor=3.0)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
