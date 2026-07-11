"""轻量数据源审计脚本 — 只读表头、前几行、行列数、缺失率、候选目标字段。"""

import os
import sys
import io
from pathlib import Path
import csv
import json

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RAW_DIR = Path(__file__).parent / "data" / "raw"

def find_csv_files(root: Path, max_depth: int = 6) -> list[Path]:
    """递归查找 CSV 文件。"""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        depth = str(dirpath).count(os.sep) - str(root).count(os.sep)
        if depth > max_depth:
            dirnames.clear()
            continue
        for f in filenames:
            if f.lower().endswith(".csv"):
                results.append(Path(dirpath) / f)
    return sorted(results)

def read_csv_header(path: Path, encoding: str = "utf-8", n_rows: int = 5) -> dict:
    """读取 CSV 表头和前几行。"""
    try:
        with open(path, encoding=encoding, errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            rows = []
            for i, row in enumerate(reader):
                if i >= n_rows:
                    break
                rows.append(row)
        return {"header": header, "sample_rows": rows, "error": None}
    except Exception as e:
        return {"header": [], "sample_rows": [], "error": str(e)}

def count_rows(path: Path, encoding: str = "utf-8") -> int:
    """快速计数行数（不加载全部数据）。"""
    try:
        with open(path, encoding=encoding, errors="replace") as f:
            return sum(1 for _ in f) - 1  # 减去表头
    except:
        return -1

def identify_mc_fields(header: list[str]) -> list[str]:
    """识别可能的 MC-LR / microcystin / toxin 相关字段。"""
    mc_keywords = [
        "mc", "microcystin", "microcyst", "toxin", "mclr", "mc_lr", "mc-lr",
        "micx", "cyanotoxin", "total_micro", "ppia",
    ]
    found = []
    for col in header:
        col_lower = col.lower().strip()
        for kw in mc_keywords:
            if kw in col_lower:
                found.append(col)
                break
    return found

def identify_time_fields(header: list[str]) -> list[str]:
    time_keywords = [
        "date", "time", "year", "month", "day", "datetime", "timestamp",
        "采样日期", "日期", "时间",
    ]
    return [col for col in header if any(kw in col.lower() for kw in time_keywords)]

def identify_location_fields(header: list[str]) -> list[str]:
    loc_keywords = [
        "lat", "lon", "lng", "long", "coord", "station", "site",
        "location", "lake", "basin", "纬度", "经度", "站点", "采样点",
    ]
    return [col for col in header if any(kw in col.lower() for kw in loc_keywords)]

def main():
    csv_files = find_csv_files(RAW_DIR)
    print(f"找到 {len(csv_files)} 个 CSV 文件\n")

    results = []
    for path in csv_files:
        rel = path.relative_to(RAW_DIR)
        print(f"--- {rel} ---")

        # 尝试 utf-8, latin1
        info = None
        for enc in ["utf-8-sig", "utf-8", "latin1"]:
            info = read_csv_header(path, encoding=enc, n_rows=3)
            if info["error"] is None and info["header"]:
                break

        if info is None or info["error"]:
            print(f"  错误: {info['error'] if info else '无法读取'}")
            results.append({"file": str(rel), "error": info["error"] if info else "read error"})
            continue

        header = info["header"]
        n_cols = len(header)
        n_rows = count_rows(path)

        mc_fields = identify_mc_fields(header)
        time_fields = identify_time_fields(header)
        loc_fields = identify_location_fields(header)

        print(f"  列数: {n_cols}, 行数: {n_rows}")
        print(f"  表头前10列: {header[:10]}")
        if mc_fields:
            print(f"  ** MC/毒素候选字段: {mc_fields}")
        if time_fields:
            print(f"  时间字段: {time_fields}")
        if loc_fields:
            print(f"  位置字段: {loc_fields}")
        print()

        results.append({
            "file": str(rel),
            "n_rows": n_rows,
            "n_cols": n_cols,
            "header": header,
            "mc_fields": mc_fields,
            "time_fields": time_fields,
            "location_fields": loc_fields,
            "sample_rows": info["sample_rows"][:2],
        })

    # 保存 JSON 结果
    out_path = Path(__file__).parent / "data" / "docs" / "_audit_raw_csv_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {out_path}")

if __name__ == "__main__":
    main()
