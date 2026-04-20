import json
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import CLEANED_DIR
from src.datasets import (
    cleo,
    emls_europe,
    gull_lake,
    sf_estuary,
    v2_erie_summary,
    v2_esp_sensor,
    v2_habs_prediction,
    v2_habs_training,
    v2_lake_erie,
    v2_sb_weekly,
    v2_toxin_models,
)
from src.logger import log_error, log_info, log_success


def clean_single(
    name: str, clean_fn: Callable[[], dict | list]
) -> tuple[str, dict | list]:
    log_info(f"[{name}] 开始清洗...")
    start = time.time()
    try:
        report = clean_fn()
        elapsed = time.time() - start
        log_success(f"[{name}] 完成 ({elapsed:.1f}s)")
        return name, report
    except Exception as e:
        log_error(f"[{name}] 失败: {e}")
        return name, {"error": str(e)}


def save_summary(results: dict, filename: str) -> None:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    path = CLEANED_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log_success(f"报告已保存: {path}")


def main() -> None:
    start = time.time()

    # 第一版本
    v1_cleaners: dict[str, Callable] = {
        "sf_estuary": sf_estuary.clean,
        "emls_europe": emls_europe.clean,
        "gull_lake": gull_lake.clean,
        "cleo": cleo.clean,
    }

    # 第二版本
    v2_cleaners: dict[str, Callable] = {
        "lake_erie": v2_lake_erie.clean,
        "esp_sensor": v2_esp_sensor.clean,
        "sb_weekly": v2_sb_weekly.clean,
        "habs_prediction": v2_habs_prediction.clean,
        "habs_training": v2_habs_training.clean,
        "erie_summary": v2_erie_summary.clean,
    }

    all_cleaners = {**v1_cleaners, **v2_cleaners}

    results: dict = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(clean_single, name, fn): name
            for name, fn in all_cleaners.items()
        }
        for future in as_completed(futures):
            name, report = future.result()
            results[name] = report

    # MC + MIX 批量清洗
    log_info("[toxin_models] 开始清洗 MC + MIX...")
    t0 = time.time()
    try:
        toxin_reports = v2_toxin_models.clean()
        results["toxin_models"] = toxin_reports
        log_success(f"[toxin_models] 完成 ({time.time() - t0:.1f}s)")
    except Exception as e:
        log_error(f"[toxin_models] 失败: {e}")
        results["toxin_models"] = {"error": str(e)}

    save_summary(results, "quality_report.json")

    elapsed = time.time() - start
    log_success(f"全部完成 ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
