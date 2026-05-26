import pandas as pd

from src.clean import (
    generate_quality_report,
    load_csv_safe,
    save_cleaned,
)
from src.config import get_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_configs()["gull_lake"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path, comment=cfg.comment_char)

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
