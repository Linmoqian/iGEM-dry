"""将 external_raw 下的数据文件统一转换为 CSV。

范围：
- *.txt / *.dat / *.tab / *.prn 等文本表格：自动检测分隔符（tab/逗号），跳过非表格的说明/元数据文件
- *.xlsx / *.xls：逐 sheet 转换，sheet 名写入文件名
- 重复文件（相同内容）：只转换一次，后续记为 duplicate
- 其它非表格格式（图片/PDF/文档/zip/shapefile 等）：不转换，报告中说明原因

输出：与源文件同目录的 converted/ 子目录（保留相对结构），
报告：data/conversion_reports/convert_report_<时间戳>.json + 汇总 md
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import shutil
import sys
from pathlib import Path
from collections import defaultdict

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "external_raw"
REPORT_DIR = ROOT / "data" / "conversion_reports"

# 尝试读取的编码，按优先级
TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "gbk", "latin-1"]

# 分隔符检测候选
DELIMS = {
    "\t": "tab",
    ",": "comma",
    ";": "semicolon",
    "|": "pipe",
    " ": "space",
}

# 会被当作元数据/说明文档而跳过的 txt（名称特征）
SKIP_NAME_HINTS = (
    "readme", "metadata", "meta-", "metadat", "_meta", "email", "journal",
    "report", "confirmation", "source_url", "method", "datadictionary",
    "data dictionary", "dictionary", "version_history", "about",
)

# 已确认不是表格数据的文件（覆盖识别不到的）
FORCE_SKIP = {
    "USGS_Sacramento_SanJoaquin_Delta/CyanoWW_2025_DataDictionary.txt",
    "USGS_Sacramento_SanJoaquin_Delta/CyanoWW_2025_Methods.txt",
}

# 无表头、首列是站点代码的数据文件：表头为占位符，保留数据行
NO_HEADER_FILES = {
    "USGS_Cheney_Reservoir_2020/Surface_Water_Chemistry.txt",
    "USGS_Cheney_Reservoir_2022/Surface_Water_Chemistry.txt",
}

# 数据文件允许跨目录重复（不同数据集重复下发，内容相同但语义不同）
# 例：Five_River_Basins 与 North_Atlantic_Appalachian_2020 是同一批数据的两个下载
DATA_DIRS_ALLOW_DUP = {
    "USGS_Five_River_Basins",
    "USGS_North_Atlantic_Appalachian_2020",
}

HEADER_PLACEHOLDER = "column_"


def sha1_of(path: Path) -> str:
    import hashlib
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text_lines(path: Path) -> list[str] | None:
    raw = path.read_bytes()
    for enc in TEXT_ENCODINGS:
        try:
            text = raw.decode(enc)
            return text.splitlines()
        except (UnicodeDecodeError, ValueError):
            continue
    return None


# 已知无表头 / 有前置说明行 / 需要特定编码的 csv 文件：直接 pandas 读取后写出
# (encoding, skiprows, keep_na)  keep_na=False 时按原始文本整体保留，不解析
FORCE_PANDAS = {    "USGS_Oregon_Cascades_Cyanotoxins/Table_10_ELISA_Parameters_QA.csv": ("latin-1", 0, True),
    "USGS_Oregon_Cascades_Cyanotoxins/Table_11_Cyanotoxin_Extract_QA.csv": ("latin-1", 0, True),
    "USGS_Oregon_Cascades_Cyanotoxins/Table_12_Cyanotoxin_SPATTs_QA.csv": ("latin-1", 0, True),
    "USGS_Oregon_Cascades_Cyanotoxins/Table_13_Cyanobacteria_Presence.csv": ("latin-1", 0, True),
    "USGS_Oregon_Cascades_Cyanotoxins/Table_14_Field_Parameters.csv": ("latin-1", 0, True),
    "NOAA_GLERL_Lake_Erie_2012_present/0187718/2.2/data/0-data/lake_erie_habs_field_sampling_master_coordinates.csv": ("utf-8", 0, True),
    "NOAA_GLERL_Lake_Erie_2012_present/0187718/2.2/data/1-data/lake_erie_habs_field_sampling_locations/lake_erie_habs_field_sampling_master_coordinates.csv": ("utf-8", 0, True),
    "NOAA_GLERL_Lake_Erie_2012_present/0190729/1.1/data/0-data/WE04_2015_annual_summary.csv": ("latin-1", 3, True),
    "NOAA_GLERL_Lake_Erie_2012_present/0194301/1.1/data/0-data/WE08_2015_annual_summary.csv": ("latin-1", 3, True),
    "NOAA_GLERL_Lake_Erie_2012_present/0194302/1.1/data/0-data/WE13_2015_annual_summary.csv": ("latin-1", 3, True),
    "NOAA_GLERL_Lake_Erie_2012_present/0276941/2.2/data/0-data/Shareable_All_Lake_Erie_sampling_data_Updated_May2025.csv": ("latin-1", 0, True),
    "NOAA_GLERL_SaginawBay/0276093_2020-2021_HABs/field_sampling_results_2020-2021.csv": ("utf-8", 0, True),
    "USGS_Large_Rivers_2017_Microcystin/Cyanotoxins_Chl_Genetic_Readme.csv": ("utf-8", 0, False),
    "USGS_Large_Rivers_2017_Phytoplankton/Phytoplankton_Abundance_Readme.csv": ("utf-8", 0, False),
    "USGS_Large_Rivers_2017_Phytoplankton_Tally/Phytoplankton_Tally_Readme.csv": ("utf-8", 0, False),
    "USGS_Large_Rivers_2018_Microcystin/Read Me.csv": ("utf-8", 0, False),
}

# 数据字典/说明类 csv（*_Readme、Read Me）：单列说明文本，保持原样转为 csv
README_CSV_PREFIX = ("Read Me", "Readme")

# Excel 透视表文件：表头 4 行（空行+字段名+列标签+行标签），第 5 行起才是数据。
# 第 1 行保留为列名（"Row Labels" 改为 "Year" 之类的行标签名），其余表头行删除。
PIVOT_SHEETS = {
    "Deep_DO_standardized_FINAL.xlsx",
    "Deep_Temperatures_standardized_FINAL.xlsx",
    "Surface_Temperatures_standardized_FINAL.xlsx",
}
PIVOT_HEADER_ROWS = 4


def looks_like_data(lines: list[str]) -> bool:
    """判定文本文件是否包含表格数据行。"""
    tab = any("\t" in ln for ln in lines[:40])
    for ln in lines[:40]:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith('"'):
            # 引号开头：可能是"整行引用说明"（非数据），也可能是"含引号单元格的数据行"
            # 数据行在逗号分隔时会把引号字段后的逗号也带上，列数 >= 2
            if s.count('"') == 2 and len(s) < 300:
                # 恰好一对引号且不长——若是数据行应还有后续列
                rest = s.split('"', 2)[-1]
                if rest.count(",") < 2:
                    return False
            continue  # 需要更多行来判断
        if s.count("\t") >= 1:
            return True
        if s.count(",") >= 2:
            return True
        if s.count(";") >= 2 or s.count("|") >= 2:
            return True
    return False


def detect_delimiter(lines: list[str]) -> str | None:
    """在候选分隔符中选在非空行中一致性最高的。"""
    sample = [ln for ln in lines[:40] if ln.strip()]
    if not sample:
        return None
    best, best_score = None, 0.0
    for d, name in DELIMS.items():
        if d == " " and any(ln.count(" ") < 5 for ln in sample):
            continue  # 空格分隔要求行内至少有 5 个空格才可信
        counts = [ln.count(d) for ln in sample]
        consistent = sum(1 for c in counts if c > 0 and c == counts[0])
        total = len(sample)
        score = (consistent / total) * min(counts)  # 同时偏好列数多
        if score > best_score:
            best_score, best = score, d
    return best


def parse_txt_table(path: Path, lines: list[str], delim: str) -> pd.DataFrame | None:
    """从 txt 中解析出数据表。跳过前置说明行（如 citation/抬头）。"""
    header_idx = None
    ncols = None
    for i, ln in enumerate(lines[:50]):
        s = ln.strip()
        if not s:
            continue
        cells = next(csv.reader([s], delimiter=delim)) if delim != " " else s.split()
        # 表头行：分隔单元格数量 > 1，且多数单元格像列名
        if len(cells) > 1 and len(cells) == len({c.strip() for c in cells if c.strip()}):
            # 排除整行引号包裹的 citation 行：它只有一个大单元格或列数明显少
            if len(cells) >= 2:
                header_idx, ncols = i, len(cells)
                break
    if header_idx is None:
        return None
    data_rows = []
    for ln in lines[header_idx + 1:]:
        if not ln.strip():
            continue
        cells = next(csv.reader([ln], delimiter=delim)) if delim != " " else ln.split()
        if len(cells) >= ncols - 1 and len(cells) <= ncols + 10:
            cells = cells[:ncols]
            if len(cells) < ncols:
                cells += [""] * (ncols - len(cells))
            data_rows.append(cells)
    if not data_rows:
        return None
    header = lines[header_idx]
    header_cells = next(csv.reader([header], delimiter=delim)) if delim != " " else header.split()
    header_cells = header_cells[:ncols]
    return pd.DataFrame(data_rows, columns=header_cells)


def _sanitize_sheet_name(name: str) -> str:
    bad = '<>:"/\\|?*'
    s = "".join("_" if c in bad else c for c in name).strip()
    return s or "sheet"


def _safe_stem(name: str, max_len: int) -> str:
    bad = '<>:"/\\|?*'
    s = "".join("_" if c in bad else c for c in name).strip()
    return (s[:max_len] if len(s) > max_len else s) or "sheet"


def _finalize_df(df: pd.DataFrame, is_pivot: bool) -> pd.DataFrame:
    """清理 pandas 读入的表格：将首行为列名的情况提升为表头，丢弃空列空行。"""
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    df = df.reset_index(drop=True)
    if is_pivot:
        # 透视表：仅保留行标签行作为表头，其余表头行删除
        df.columns = [f"col_{i}" for i in range(df.shape[1])]
        if df.shape[0] > 0:
            header = df.iloc[PIVOT_HEADER_ROWS - 1]
            df = df.iloc[PIVOT_HEADER_ROWS:].reset_index(drop=True)
            df.columns = [str(v) if pd.notna(v) else f"col_{i}" for i, v in enumerate(header)]
        # 透视表特有的空列 (blank)/总计列（偏移的尾部），整列丢弃
        df = df.loc[:, ~df.columns.isin(["(blank)", "Grand Total"])]
        return df
    while df.shape[0] >= 1 and not df.iloc[0].notna().any():
        df = df.iloc[1:].reset_index(drop=True)
    if df.shape[0] >= 1:
        first = df.iloc[0]
        if first.notna().any() and not pd.to_numeric(first, errors="coerce").notna().all():
            df = df.iloc[1:]
            df = df.reset_index(drop=True)
            df.columns = [str(v) if pd.notna(v) else f"col_{i}" for i, v in enumerate(first)]
    return df


def convert_excel(path: Path, out_dir: Path, results: list[dict], dup_seen: dict) -> list[dict]:
    if path.suffix.lower() == ".xlsx":
        sheets = pd.read_excel(path, sheet_name=None, header=None)
    else:
        sheets = pd.read_excel(path, sheet_name=None, header=None, engine="xlrd")
    made = []
    for i, (name, df) in enumerate(sheets.items()):
        if df.empty or df.shape[1] == 0:
            results.append({
                "status": "skipped_empty_sheet", "sheet": name,
                "rows": 0, "cols": 0,
            })
            continue
        df = _finalize_df(df, is_pivot=path.name in PIVOT_SHEETS)
        df = df.where(pd.notna(df), None)
        base = _safe_stem(path.stem, 80)
        sheet = _sanitize_sheet_name(name)
        out_file = out_dir / f"{base}__{sheet}.csv"
        if out_file.exists():
            out_file = out_dir / f"{base}__{sheet}__s{i+1}.csv"
        df.to_csv(out_file, index=False, encoding="utf-8-sig")
        results.append({
            "status": "ok", "sheet": name, "rows": int(df.shape[0]),
            "cols": int(df.shape[1]), "output": str(out_file.relative_to(RAW)),
        })
        made.append(out_file)
    return made


def convert_txt(path: Path, out_dir: Path, lines: list[str], results: list[dict]) -> list[dict]:
    if not looks_like_data(lines):
        results.append({"status": "skipped_nondata_txt"})
        return []
    delim = detect_delimiter(lines)
    if delim is None:
        results.append({"status": "skipped_no_delimiter"})
        return []
    df = parse_txt_table(path, lines, delim)
    if df is None or df.empty:
        results.append({"status": "skipped_no_parseable_table", "delimiter": DELIMS[delim]})
        return []
    out_file = out_dir / f"{path.stem}.csv"
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    results.append({
        "status": "ok", "delimiter": DELIMS[delim],
        "rows": int(df.shape[0]), "cols": int(df.shape[1]),
        "output": str(out_file.relative_to(RAW)),
    })
    return [out_file]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    raw: Path = args.raw
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "raw_root": str(raw),
        "files": [],       # 每文件一条
        "counts": {},
        "special_cases": [],
    }
    seen_sha = {}  # sha1 -> first path
    dup_skipped = 0

    all_files = sorted(
        p for p in raw.rglob("*")
        if p.is_file() and "converted" not in p.parts
    )
    for path in all_files:
        rel = path.relative_to(raw)
        rec = {"file": str(rel), "size": path.stat().st_size, "ext": path.suffix.lower()}
        # 跳过 manifest 目录
        if rel.parts[0] == "_manifests":
            rec["status"] = "skipped_manifests_dir"
            summary["files"].append(rec)
            continue

        ext = path.suffix.lower()
        is_excel = ext in (".xlsx", ".xls")
        is_txtlike = ext in (".txt", ".dat", ".tab", ".prn", ".csv", ".tsv")
        if is_excel:
            rec["kind"] = "excel"
        elif is_txtlike:
            rec["kind"] = "text"
        else:
            rec["kind"] = "other"

        # 去重：仅对 excel/txt 数据文件（跨允许重复的数据集目录除外）
        if is_excel or is_txtlike:
            sha = sha1_of(path)
            top_dir = rel.parts[0] if len(rel.parts) > 1 else ""
            dup_allowed = top_dir in DATA_DIRS_ALLOW_DUP
            if sha in seen_sha and not dup_allowed:
                rec["status"] = "duplicate"
                rec["duplicate_of"] = str(seen_sha[sha])
                dup_skipped += 1
                summary["files"].append(rec)
                continue
            if sha not in seen_sha or dup_allowed:
                seen_sha[sha] = rel

        if args.dry_run:
            rec["status"] = "dry_run_planned"
            summary["files"].append(rec)
            continue

        # 非数据格式
        if not (is_excel or is_txtlike):
            if ext in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"):
                rec["status"] = "skipped_image"
            elif ext in (".pdf",):
                rec["status"] = "skipped_pdf"
            elif ext in (".docx",):
                rec["status"] = "skipped_docx"
            elif ext in (".zip",):
                rec["status"] = "skipped_zip"
            elif ext in (".shp", ".dbf", ".shx", ".prj", ".cpg", ".sbn", ".sbx"):
                rec["status"] = "skipped_shapefile"
            elif ext in (".xml", ".xsl"):
                rec["status"] = "skipped_xml"
            else:
                rec["status"] = "skipped_other_format"
            summary["files"].append(rec)
            continue

        # 文本类强制跳过清单
        rel_str = str(rel).replace("\\", "/")
        if rel_str in FORCE_SKIP:
            rec["status"] = "skipped_forced"
            summary["files"].append(rec)
            continue

        out_dir = path.parent / "converted"
        out_dir.mkdir(exist_ok=True)
        results: list[dict] = []
        try:
            if is_excel:
                convert_excel(path, out_dir, results, seen_sha)
            else:
                # 已知需要 pandas 直接读取的 csv
                if rel_str in FORCE_PANDAS:
                    enc, skip, keep_na = FORCE_PANDAS[rel_str]
                    if keep_na:
                        df = pd.read_csv(path, encoding=enc, skiprows=skip,
                                         keep_default_na=False, on_bad_lines="skip")
                        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
                    else:
                        # 说明类文件：整行读为单列，保留原文
                        raw_txt = path.read_bytes().decode(enc, errors="replace")
                        df = pd.DataFrame({"content": [ln for ln in raw_txt.splitlines()]})
                    out_file = out_dir / f"{path.stem}.csv"
                    df.to_csv(out_file, index=False, encoding="utf-8-sig")
                    results.append({
                        "status": "ok", "delimiter": "comma",
                        "rows": int(df.shape[0]), "cols": int(df.shape[1]),
                        "output": str(out_file.relative_to(RAW)),
                    })
                else:
                    lines = read_text_lines(path)
                    if lines is None:
                        rec["status"] = "error_decode"
                        summary["files"].append(rec)
                        continue
                    # 无表头文件：注入占位表头
                    if rel_str in NO_HEADER_FILES and lines:
                        ncols = max(len(l.split("\t")) for l in lines[:30])
                        lines.insert(0, "\t".join(f"{HEADER_PLACEHOLDER}{i+1}" for i in range(ncols)))
                    convert_txt(path, out_dir, lines, results)

            if not results:
                rec["status"] = "skipped"
            elif all(r["status"] == "ok" for r in results):
                rec["status"] = "ok"
                rec["n_outputs"] = len(results)
                rec["total_rows"] = sum(r.get("rows", 0) for r in results)
            else:
                rec["status"] = "partial"
            rec["details"] = results
        except Exception as e:  # noqa: BLE001
            rec["status"] = "error"
            rec["error"] = f"{type(e).__name__}: {e}"
        summary["files"].append(rec)

    # 汇总计数
    counts = defaultdict(int)
    by_status_ext = defaultdict(int)
    for rec in summary["files"]:
        counts[rec["status"]] += 1
        by_status_ext[(rec["status"], rec.get("kind", ""))] += 1
    summary["counts"] = dict(counts)
    summary["counts_by_kind"] = {f"{s}/{k}": v for (s, k), v in sorted(by_status_ext.items())}
    summary["duplicates_skipped"] = dup_skipped
    ok_rows = sum(r.get("total_rows", 0) for r in summary["files"] if r["status"] == "ok")
    summary["ok_total_rows"] = ok_rows

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_out = REPORT_DIR / f"convert_report_{stamp}.json"
    json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # 汇总 md
    md = REPORT_DIR / "CONVERSION_REPORT.md"
    lines_md = [f"# 数据转换报告（{stamp}）", "",
                f"- 转换成功：{counts['ok']} 个文件",
                f"- 跳过（非数据/元数据/重复/其它格式）：{counts['skipped'] + counts['skipped_nondata_txt'] + dup_skipped + counts['skipped_other_format']} 个文件",
                f"- 失败：{counts['error']} 个文件",
                f"- 成功转换行数合计：{ok_rows:,}", "",
                "## 失败列表", ""]
    for rec in summary["files"]:
        if rec["status"] == "error":
            lines_md.append(f"- {rec['file']} — {rec.get('error', '')}")
    md.write_text("\n".join(lines_md), encoding="utf-8")
    print(f"report: {json_out}")
    print(f"md: {md}")
    print(f"ok={counts['ok']} error={counts['error']} dup={dup_skipped} "
          f"skipped={counts['skipped']} other={counts['skipped_other_format']}")


if __name__ == "__main__":
    main()
