import pandas as pd

from src.clean import (
    generate_quality_report,
    load_csv_safe,
    save_cleaned,
)
from src.config import get_v2_configs
from src.logger import log_info


def clean() -> list[dict]:
    """清洗 MC 和 MIX 共 4 个数据集，返回报告列表。"""
    configs = get_v2_configs()
    reports = []

    datasets = ["mc_data", "mc_env", "mix_data", "mix_env"]
    for key in datasets:
        cfg = configs[key]
        log_info(f"开始清洗: {cfg.name}")

        df = load_csv_safe(cfg.raw_path)

        # 解析日期时间
        if "DateTime" in df.columns:
            df["DateTime"] = pd.to_datetime(
                df["DateTime"], format="mixed", errors="coerce"
            )

        report = generate_quality_report(df, cfg.name)
        save_cleaned(df, cfg.output_name, report)
        reports.append(report)

    return reports
