import pandas as pd

from src.clean import (
    generate_quality_report,
    parse_multirow_header_csv,
    replace_detection_limits,
    save_cleaned,
)
from src.config import get_v2_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_v2_configs()["erie_summary"]
    log_info(f"开始清洗: {cfg.name}")

    # 用专用函数解析多行表头
    df = parse_multirow_header_csv(
        cfg.raw_path, header_rows=7, encoding=cfg.encoding
    )

    # 需要处理检测限标记的列
    detection_cols = [
        col for col in df.columns
        if any(
            kw in str(col)
            for kw in ["Microcystin", "Secchi", "Temp", "Cond", "CHL",
                       "PC", "PAR", "DO", "Turbidity", "Total P", "TDP",
                       "SRP", "NH4", "NO3", "Urea", "SiO2", "TSS", "VSS",
                       "POC", "PON", "DOC", "Cyanos", "Transmission"]
        )
    ]
    for col in detection_cols:
        df = replace_detection_limits(df, column=col, strategy="nan")

    # 处理带问号的可疑值 (如 '2778.75 ?294')
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"\s*\?.*$", "", regex=True)
            )
            # 尝试转为数值
            df[col] = pd.to_numeric(df[col], errors="coerce")

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
