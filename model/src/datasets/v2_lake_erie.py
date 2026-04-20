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
    cfg = get_v2_configs()["lake_erie"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path, encoding=cfg.encoding)

    # 删除空列和高缺失列
    df = drop_high_missing_columns(df, columns=cfg.columns_to_drop)

    # 检测限标记: '< 0.15' / '<0.15' -> 半检测限
    df = replace_detection_limits(
        df, column="Total Microcystins (ug/L)", strategy="half"
    )
    df = replace_detection_limits(
        df, column="Extracellular Microcystin (ug/L)", strategy="half"
    )

    # Program 名标准化
    program_fixes = {
        "SL Bouy": "SL Buoy",
        "HABsGrab": "HABs Grab",
    }
    col = "Program"
    if col in df.columns:
        needs_copy = any(
            (df[col] == wrong).any() for wrong in program_fixes
        )
        if needs_copy:
            df = df.copy()
            for wrong, correct in program_fixes.items():
                mask = df[col] == wrong
                n = mask.sum()
                if n > 0:
                    df.loc[mask, col] = correct
                    log_info(f"Program 修正: '{wrong}' -> '{correct}' ({n} 条)")

    # 解析日期
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
