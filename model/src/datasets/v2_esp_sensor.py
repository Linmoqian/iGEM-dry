import pandas as pd

from src.clean import (
    drop_high_missing_columns,
    generate_quality_report,
    load_csv_safe,
    replace_detection_limits,
    save_cleaned,
)
from src.config import get_v2_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_v2_configs()["esp_sensor"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path)

    # 删除全空列
    df = drop_high_missing_columns(df, columns=cfg.columns_to_drop)

    # MC 列检测限标记处理
    df = replace_detection_limits(df, column="MC ug L-1", strategy="nan")

    # depth 标记为分类变量
    if "depth" in df.columns:
        df["depth"] = pd.Categorical(df["depth"].astype(str).str.strip())

    # 解析日期
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
