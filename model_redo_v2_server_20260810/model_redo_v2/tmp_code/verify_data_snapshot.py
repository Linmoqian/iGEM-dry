"""Hash the copied data snapshot and optionally compare it to model_redo source data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "data"
DEFAULT_SOURCE = ROOT.parent / "model_redo" / "data" / "data_processed"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(2**20):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, dict]:
    result = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        result[relative] = {"relative_path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)}
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "references")
    args = parser.parse_args()
    target = args.target.resolve()
    source = args.source.resolve()
    target_rows = inventory(target)
    source_rows = inventory(source) if source.exists() else {}
    rows = []
    mismatches = []
    for relative, row in target_rows.items():
        source_row = source_rows.get(relative)
        copied_exactly = None if not source_rows else source_row == row
        rows.append({**row, "copied_exactly": copied_exactly})
        if copied_exactly is False:
            mismatches.append(relative)
    missing = sorted(set(source_rows) - set(target_rows))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "data_snapshot_manifest.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "bytes", "sha256", "copied_exactly"])
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "target": str(target),
        "source": str(source) if source.exists() else None,
        "target_files": len(target_rows),
        "target_bytes": sum(row["bytes"] for row in target_rows.values()),
        "source_files": len(source_rows) if source_rows else None,
        "source_bytes": sum(row["bytes"] for row in source_rows.values()) if source_rows else None,
        "hash_mismatches": mismatches,
        "missing_in_target": missing,
        "exact_copy": bool(source_rows)
        and not mismatches
        and not missing
        and len(source_rows) == len(target_rows),
    }
    (args.output_dir / "data_snapshot_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not source_rows or summary["exact_copy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
