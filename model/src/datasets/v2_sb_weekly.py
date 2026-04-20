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
    cfg = get_v2_configs()["sb_weekly"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path)

    # 删除全空列
    df = drop_high_missing_columns(df, columns=cfg.columns_to_drop)

    # 检测限标记处理
    detection_limit_cols = [
        "DO_mgL-1",
        "Turbidity_NTU",
        "Particulate_Microcystin_ugL-1",
        "Dissolved_Microcystin_ugL-1",
        "Secchi_Depth_m",
        "Extracted_PC_ugL-1",
        "Extracted_CHLa_ugL-1",
    ]
    for col in detection_limit_cols:
        if col in df.columns:
            df = replace_detection_limits(df, column=col, strategy="nan")

    # 解析日期
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
