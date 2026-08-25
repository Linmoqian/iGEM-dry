"""将 model_redo/data/raw 下的数据文件统一转换为 CSV。

范围（与 external_raw 转换策略一致）：
- *.txt 文本表格：自动检测分隔符（tab/逗号），转 CSV；纯说明/元数据跳过
- *.xlsx / *.xls：逐 sheet 转换
- *.mat：EMS 模型模拟数据（MOD/OBS/PreD 数组），转 CSV
- 压缩包内的 *.xlsx：MC/MIX 模型原始数据，解压读取转 CSV
- 其它格式（shapefile/gdb/pdf/jpg 等）：跳过

输出：与源文件同目录的 converted/ 子目录（保留相对结构）
"""
from __future__ import annotations

import csv
import datetime
import glob
import io
import json
import os
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "data" / "conversion_reports"

TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "gbk", "latin-1"]
DELIMS = {"\t": "tab", ",": "comma", ";": "semicolon", "|": "pipe"}

# 名称特征：说明/元数据类 txt 跳过
SKIP_NAME_HINTS = (
    "readme", "metadata", "_meta", "meta-", "email", "journal", "report",
    "confirmation", "source_url", "方法", "网站", "manifest", "说明",
)

# 已确认是说明文档而非数据表的文件
FORCE_SKIP_TXT = {
    "NLA 2022/58_WSA_All_Data__(zip)/phabmet.txt",          # SAS CONTENTS 输出
    "NLA 2022/58_WSA_All_Data__(zip)/wsaallsites.sas",      # SAS 脚本
}


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
            return raw.decode(enc).splitlines()
        except (UnicodeDecodeError, ValueError):
            continue
    return None


def looks_like_data(lines: list[str]) -> bool:
    """判定文本文件是否包含表格数据行（与 external_raw 相同逻辑）。"""
    for ln in lines[:40]:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith('"'):
            if s.count('"') == 2 and len(s) < 300:
                rest = s.split('"', 2)[-1]
                if rest.count(",") < 2:
                    return False
            continue
        if s.count("\t") >= 1 or s.count(",") >= 2 or s.count(";") >= 2 or s.count("|") >= 2:
            return True
    return False


def detect_delimiter(lines: list[str]) -> str | None:
    sample = [ln for ln in lines[:40] if ln.strip()]
    if not sample:
        return None
    best, best_score = None, 0.0
    for d in DELIMS:
        counts = [ln.count(d) for ln in sample]
        consistent = sum(1 for c in counts if c > 0 and c == counts[0])
        score = (consistent / len(sample)) * min(counts)
        if score > best_score:
            best_score, best = score, d
    return best


def parse_txt_table(lines: list[str], delim: str) -> pd.DataFrame | None:
    header_idx, ncols = None, None
    for i, ln in enumerate(lines[:50]):
        s = ln.strip()
        if not s:
            continue
        cells = next(csv.reader([s], delimiter=delim))
        if len(cells) > 1 and len(cells) == len({c.strip() for c in cells if c.strip()}):
            header_idx, ncols = i, len(cells)
            break
    if header_idx is None:
        return None
    data_rows = []
    for ln in lines[header_idx + 1:]:
        if not ln.strip():
            continue
        cells = next(csv.reader([ln], delimiter=delim))
        if len(cells) >= ncols - 1 and len(cells) <= ncols + 10:
            cells = cells[:ncols]
            if len(cells) < ncols:
                cells += [""] * (ncols - len(cells))
            data_rows.append(cells)
    if not data_rows:
        return None
    header_cells = next(csv.reader([lines[header_idx]], delimiter=delim))[:ncols]
    return pd.DataFrame(data_rows, columns=header_cells)


def _finalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all").reset_index(drop=True)
    while df.shape[0] >= 1 and not df.iloc[0].notna().any():
        df = df.iloc[1:].reset_index(drop=True)
    if df.shape[0] >= 1:
        first = df.iloc[0]
        if first.notna().any() and not pd.to_numeric(first, errors="coerce").notna().all():
            df = df.iloc[1:].reset_index(drop=True)
            df.columns = [str(v) if pd.notna(v) else f"col_{i}" for i, v in enumerate(first)]
    return df


def _safe_stem(name: str, max_len: int = 100) -> str:
    bad = '<>:"/\\|?*'
    s = "".join("_" if c in bad else c for c in name).strip()
    return (s[:max_len] if len(s) > max_len else s) or "sheet"


def _sanitize_sheet_name(name: str) -> str:
    bad = '<>:"/\\|?*'
    s = "".join("_" if c in bad else c for c in name).strip()
    return s or "sheet"


def convert_excel_bytes(data: bytes, stem: str, out_dir: Path, results: list[dict]) -> None:
    sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None)
    for i, (name, df) in enumerate(sheets.items()):
        if df.empty or df.shape[1] == 0:
            continue
        df = _finalize_df(df)
        df = df.where(pd.notna(df), None)
        out_file = out_dir / f"{_safe_stem(stem)}__{_sanitize_sheet_name(name)}.csv"
        if out_file.exists():
            out_file = out_dir / f"{_safe_stem(stem)}__{_sanitize_sheet_name(name)}__s{i+1}.csv"
        df.to_csv(out_file, index=False, encoding="utf-8-sig")
        results.append({"status": "ok", "sheet": name, "rows": int(df.shape[0]),
                        "cols": int(df.shape[1]), "output": str(out_file.relative_to(RAW))})


def convert_mat(path: Path, out_dir: Path, results: list[dict]) -> None:
    import scipy.io
    m = scipy.io.loadmat(str(path))
    for key in ["MOD", "OBS", "PreD"]:
        if key not in m:
            continue
        arr = np.asarray(m[key])
        df = pd.DataFrame(arr)
        out_file = out_dir / f"{path.stem}__{key}.csv"
        df.to_csv(out_file, index=False, encoding="utf-8-sig")
        results.append({"status": "ok", "mat_key": key, "rows": int(arr.shape[0]),
                        "cols": int(arr.shape[1]), "output": str(out_file.relative_to(RAW))})


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "raw_root": str(RAW),
        "files": [],
        "counts": {},
    }
    seen_sha = {}
    all_files = sorted(p for p in RAW.rglob("*") if p.is_file() and "converted" not in p.parts)

    for path in all_files:
        rel = path.relative_to(RAW)
        rel_str = str(rel).replace("\\", "/")
        rec = {"file": rel_str, "size": path.stat().st_size, "ext": path.suffix.lower()}
        ext = path.suffix.lower()
        is_excel = ext in (".xlsx", ".xls")
        is_txtlike = ext in (".txt", ".dat", ".tab", ".prn", ".tsv")
        is_mat = ext == ".mat"

        # 去重
        if is_excel or is_txtlike or is_mat:
            sha = sha1_of(path)
            if sha in seen_sha:
                rec["status"] = "duplicate"
                rec["duplicate_of"] = str(seen_sha[sha])
                summary["files"].append(rec)
                continue
            seen_sha[sha] = rel

        if not (is_excel or is_txtlike or is_mat):
            if ext in (".jpg", ".jpeg", ".png", ".bmp", ".tif"):
                rec["status"] = "skipped_image"
            elif ext == ".pdf":
                rec["status"] = "skipped_pdf"
            elif ext in (".docx", ".doc"):
                rec["status"] = "skipped_docx"
            elif ext == ".zip":
                rec["status"] = "skipped_zip"
            elif ext in (".shp", ".dbf", ".shx", ".prj", ".cpg", ".sbn", ".sbx", ".atx", ".gdbindexes", ".gdbtable", ".gdbtablx", ".freelist", ".spx", ".lock"):
                rec["status"] = "skipped_gis"
            elif ext in (".xml", ".xsl", ".gz", ".matx"):
                rec["status"] = "skipped_xml"
            elif ext in (".sas", ".py", ".js", ".json", ".md"):
                rec["status"] = "skipped_code_doc"
            else:
                rec["status"] = "skipped_other_format"
            summary["files"].append(rec)
            continue

        if rel_str in FORCE_SKIP_TXT:
            rec["status"] = "skipped_forced"
            summary["files"].append(rec)
            continue

        out_dir = path.parent / "converted"
        out_dir.mkdir(exist_ok=True)
        results: list[dict] = []
        try:
            if is_excel:
                convert_excel_bytes(path.read_bytes(), path.stem, out_dir, results)
            elif is_mat:
                convert_mat(path, out_dir, results)
            else:
                # txt 类：跳过说明文档
                lines = read_text_lines(path)
                if lines is None:
                    rec["status"] = "error_decode"
                    summary["files"].append(rec)
                    continue
                if not looks_like_data(lines):
                    rec["status"] = "skipped_nondata_txt"
                    summary["files"].append(rec)
                    continue
                delim = detect_delimiter(lines)
                if delim is None:
                    rec["status"] = "skipped_no_delimiter"
                    summary["files"].append(rec)
                    continue
                df = parse_txt_table(lines, delim)
                if df is None or df.empty:
                    rec["status"] = "skipped_no_parseable_table"
                    summary["files"].append(rec)
                    continue
                out_file = out_dir / f"{path.stem}.csv"
                df.to_csv(out_file, index=False, encoding="utf-8-sig")
                results.append({"status": "ok", "delimiter": DELIMS[delim],
                                "rows": int(df.shape[0]), "cols": int(df.shape[1]),
                                "output": str(out_file.relative_to(RAW))})

            if not results:
                rec["status"] = "skipped"
            elif all(r["status"] == "ok" for r in results):
                rec["status"] = "ok"
                rec["n_outputs"] = len(results)
                rec["total_rows"] = sum(r.get("rows", 0) for r in results)
            else:
                rec["status"] = "partial"
            rec["details"] = results
        except Exception as e:
            rec["status"] = "error"
            rec["error"] = f"{type(e).__name__}: {e}"
        summary["files"].append(rec)

    counts = defaultdict(int)
    for rec in summary["files"]:
        counts[rec["status"]] += 1
    summary["counts"] = dict(counts)
    summary["ok_total_rows"] = sum(r.get("total_rows", 0) for r in summary["files"] if r["status"] == "ok")

    # zip 内 xlsx 的转换
    zip_conv = {"converted": [], "counts": defaultdict(int)}
    for z in sorted((RAW / "数据汇总v2(clf)" / "1.数据汇总" / "08_压缩包").glob("*.zip")):
        if "交叉验证" in z.name or "概率预测" in z.name:
            continue
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                if n.endswith(".xlsx"):
                    out_dir = RAW / "数据汇总v2(clf)" / "1.数据汇总" / "08_压缩包" / "converted"
                    out_dir.mkdir(exist_ok=True)
                    results = []
                    convert_excel_bytes(zf.read(n), z.stem + "_" + Path(n).stem, out_dir, results)
                    for r in results:
                        zip_conv["converted"].append({"zip": z.name, **r})
                        zip_conv["counts"]["ok"] += 1
    summary["zip_inner_xlsx"] = {
        "converted": zip_conv["converted"],
        "ok": zip_conv["counts"]["ok"],
    }

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_out = REPORT_DIR / f"raw_convert_report_{stamp}.json"
    json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"report: {json_out}")
    print(f"ok={counts['ok']} skipped_nondata={counts['skipped_nondata_txt']} "
          f"dup={counts['duplicate']} error={counts['error']} other={sum(v for k, v in counts.items() if k.startswith('skipped'))}")


if __name__ == "__main__":
    main()
