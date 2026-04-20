import pandas as pd

from src.clean import (
    generate_quality_report,
    load_csv_safe,
    save_cleaned,
)
from src.config import get_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_configs()["cleo"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path)

    df["toxin_level"] = pd.Categorical(
        df["toxin_level"].astype(int), categories=[1, 2, 3, 4], ordered=True
    )

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
