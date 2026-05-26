from src.clean import (
    generate_quality_report,
    load_csv_safe,
    replace_sentinel_values,
    save_cleaned,
)
from src.config import get_v2_configs
from src.logger import log_info


def clean() -> dict:
    cfg = get_v2_configs()["habs_prediction"]
    log_info(f"开始清洗: {cfg.name}")

    df = load_csv_safe(cfg.raw_path)

    # -1000 哨兵值替换
    sentinel_cols = [
        "micx_logit.fit",
        "micx_logit.lwr",
        "micx_logit.upr",
        "micx_prob.fit",
        "micx_prob.lwr",
        "micx_prob.upr",
        "cyano_log.fit",
        "cyano_log.lwr",
        "cyano_log.upr",
        "cyano_abun.fit",
        "cyano_abun.lwr",
        "cyano_abun.upr",
    ]
    df = replace_sentinel_values(df, columns=sentinel_cols, sentinel=-1000)

    report = generate_quality_report(df, cfg.name)
    save_cleaned(df, cfg.output_name, report)
    return report
