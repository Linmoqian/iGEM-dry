"""Build a consolidated dataset survey MD in model_redo/data/external_raw/.

Reads the final download inventory + per-dataset READMEs + v2 dataset manifest,
and writes 数据集调研与下载汇总.md (dataset name, content, suitability, links, download status).
"""
from __future__ import annotations

import os
import re
import json
from pathlib import Path

import pandas as pd

MR = Path(__file__).resolve().parents[2] / "model_redo"
EXT = MR / "data" / "external_raw"
INV = EXT / "_manifests/full_download_manifest_2026-08-06_final_inventory_rerun_2026-08-06.csv"
V2_MANIFEST = Path(__file__).resolve().parents[1] / "data/catalog/dataset_manifest.csv"

inv = pd.read_csv(INV)
try:
    v2m = pd.read_csv(V2_MANIFEST)
    toxin_hint = dict(zip(v2m["dataset"].astype(str), v2m.get("has_toxin_hint", pd.Series(index=v2m.index))))
    role = dict(zip(v2m["dataset"].astype(str), v2m.get("role", pd.Series(index=v2m.index))))
except Exception:
    toxin_hint, role = {}, {}

def urls_from_readme(dataset: str, limit: int = 6):
    readme = EXT / dataset / "README.md"
    if not readme.exists():
        readme = EXT / dataset / "_README.md"
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8", errors="ignore")
    found = re.findall(r"(?:https?://|www\.)[^\s\\)\]\"'<>]+", text)
    out = []
    for u in found:
        u = u.rstrip(".,;")
        if u.startswith("www."):
            u = "https://" + u
        if u not in out:
            out.append(u)
    return out[:limit]

rows = []
for dataset in sorted({d for d in inv["dataset"].astype(str) if d}):
    sub = inv[inv["dataset"].astype(str) == dataset]
    statuses = sub["status"].value_counts().to_dict()
    paths = EXT / dataset
    has_dir = paths.is_dir()
    bytes_total = int(sub["size_bytes"].sum()) if "size_bytes" in sub else 0
    files_local = len(list(paths.rglob("*"))) if has_dir else 0
    urls = urls_from_readme(dataset)
    rows.append({
        "dataset": dataset,
        "files_inventory": int(len(sub)),
        "files_dir": files_local,
        "bytes_mib": round(bytes_total / 1024 / 1024, 2),
        "statuses": " / ".join(f"{k}:{v}" for k, v in sorted(statuses.items())),
        "toxin_hint": int(toxin_hint.get(dataset, -1)),
        "role": str(role.get(dataset, "-")),
        "links": " / ".join(urls) if urls else "-",
    })

extra = []
for d in sorted(p.name for p in EXT.iterdir() if p.is_dir() and not p.name.startswith("_")):
    if d not in {r["dataset"] for r in rows}:
        n = len(list((EXT / d).rglob("*")))
        extra.append((d, n))

lines = []
lines.append("# 外部数据集调研、适配性与下载汇总")
lines.append("")
lines.append("- 汇总日期：2026-08-11（模型审查轮次 R9 补写，数据均为既有资产，无新增下载）")
lines.append("- 完整机器清单：_manifests/full_download_manifest_2026-08-06_final_inventory_rerun_2026-08-06.csv（每条文件含来源 URL、本地路径、SHA-256）")
lines.append("- 历史下载过程报告：_manifests/下载汇总报告_2026-08-06.md、../../reports/external_dataset_download_status_2026-08-06.md")
lines.append("- 数据集角色定义：toxin_hint=1 表示该数据集含毒素浓度提示列；role 为 v2 数据目录中的处理角色")
lines.append("")
lines.append(f"合计：{len(rows)} 个数据集目录（含清单记录），清单文件 {sum(r['files_inventory'] for r in rows)} 个，约 {sum(r['bytes_mib'] for r in rows):,.1f} MiB。另有 {len(extra)} 个环境/遥感资产目录（清单独立记录）。")
lines.append("")
lines.append("| 数据集 | 清单文件数 | 本地目录文件数 | 容量(MiB) | 状态(存在/缺失/受限) | 毒素提示 | 建模角色 | 官方链接(来自数据集 README) |")
lines.append("|---|---|---:|---:|---|---|---|---|")
for r in rows:
    links = r["links"] if r["links"] != "-" else "（见目录内 README）"
    lines.append(f"| {r['dataset']} | {r['files_inventory']} | {r['files_dir']} | {r['bytes_mib']:,.2f} | {r['statuses']} | {r['toxin_hint']} | {r['role']} | {links} |")
lines.append("")
lines.append("## 目录中但未出现在最终清单的数据集目录（多为环境/遥感资产，单独记录）")
lines.append("")
for name, n in extra:
    lines.append(f"- {name}（{n} 个文件）")
lines.append("")
lines.append("## 下载情况结论")
lines.append("")
lines.append("1. **可直接使用的建模数据**：EPA NLA/NCCA/NRSA/NWCA 系列、USGS ScienceBase 系列（Erie、Sacramento、Cheney、Large Rivers、WQP 等）、NOAA GLERL/NCEI、法国 data.gouv、Zenodo Clear Lake 等均已落盘并通过 SHA-256 校验。")
lines.append("2. **未能完整下载的官方对象**：ScienceBase 11 个 404 对象、USGS Phytoplankton_Tally.xlsx（约 837 MB 不可续传）、Dryad Uruguay、USDA Georgia Figshare、Alberta、Figshare Buley Global Microcystin、Figshare 中国长期水质（持续 WAF/Cloudflare 403）。")
lines.append("3. **结论与限制**：现有数据足以支撑‘总 MC 跨来源概率建模 + MC-LR 受限建模 + 中国域协变量对齐’；不足以支撑单纯依靠现有文件完成东湖本地 MC-LR 高精度预测。")
lines.append("")
STAMP = EXT / "数据集调研与下载汇总.md"
STAMP.write_text("\n".join(lines), encoding="utf-8")
print("written", STAMP)
print("rows", len(rows), "extra", len(extra))