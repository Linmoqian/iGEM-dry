"""Run repeated non-IID outer folds and aggregate auditable model metrics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cmadre.config import load_config
from cmadre.pipeline import run_training


def _nested(payload: dict, *keys):
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _run_row(run_dir: Path, repeat: int, fold: int, seed: int) -> dict:
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    stack = json.loads((run_dir / "stacking_weights.json").read_text(encoding="utf-8"))
    test = metrics["test"]["ensemble_calibrated"]
    point = test["point"]
    row = {
        "repeat": repeat,
        "test_fold": fold,
        "seed": seed,
        "run_dir": str(run_dir),
        "rows": test.get("rows"),
        "exact_rows": test.get("exact_rows"),
        "censored_rows": test.get("censored_rows"),
        "log1p_mae": point.get("log1p_mae"),
        "log1p_rmse": point.get("log1p_rmse"),
        "mae_ug_l": point.get("mae_ug_l"),
        "median_ae_ug_l": point.get("median_ae_ug_l"),
        "rmse_ug_l": point.get("rmse_ug_l"),
        "r2": point.get("r2"),
        "spearman": point.get("spearman"),
        "within_factor_2": point.get("within_factor_2"),
        "source_macro_log1p_mae": test.get("source_macro_log1p_mae"),
        "worst_source_log1p_mae": test.get("worst_source_log1p_mae"),
        "interval_distance_mae_ug_l": test.get("interval_distance_mae_ug_l"),
        "exact_q10_q90_coverage": test.get("exact_q10_q90_coverage"),
        "exact_q10_q90_mean_width_ug_l": test.get("exact_q10_q90_mean_width_ug_l"),
        "observation_interval_compatibility": test.get("observation_interval_compatibility"),
        "ood_rate": _nested(metrics, "ood", "test_flag_rate"),
        "tail90_log1p_mae": _nested(test, "tail_diagnostics", "q90", "log1p_mae"),
        "tail90_mae_ug_l": _nested(test, "tail_diagnostics", "q90", "mae_ug_l"),
        "tail95_log1p_mae": _nested(test, "tail_diagnostics", "q95", "log1p_mae"),
        "tail99_log1p_mae": _nested(test, "tail_diagnostics", "q99", "log1p_mae"),
    }
    for model, weight in stack["weights"].items():
        row[f"weight__{model}"] = weight
    for model, model_metrics in metrics["test"]["base_models"].items():
        row[f"base_log1p_mae__{model}"] = _nested(model_metrics, "point", "log1p_mae")
    return row


def _aggregate(frame: pd.DataFrame) -> dict:
    excluded = {"repeat", "test_fold", "seed", "run_dir"}
    result = {"fold_runs": len(frame), "numeric": {}}
    for column in frame.columns:
        if column in excluded:
            continue
        values = pd.to_numeric(frame[column], errors="coerce").dropna()
        if len(values):
            result["numeric"][column] = {
                "count": len(values),
                "mean": float(values.mean()),
                "std": float(values.std(ddof=0)),
                "min": float(values.min()),
                "max": float(values.max()),
                "median": float(values.median()),
            }
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--repeat-start", type=int, default=0)
    parser.add_argument("--folds", help="comma-separated fold IDs; default is every fold")
    parser.add_argument("--seed-stride", type=int, default=1009)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    base = load_config(args.config)
    n_folds = int(base["n_folds"])
    folds = list(range(n_folds)) if not args.folds else [int(v) for v in args.folds.split(",")]
    if not folds or any(fold < 0 or fold >= n_folds for fold in folds):
        raise ValueError("fold IDs must be within configured n_folds")
    if args.repeats < 1:
        raise ValueError("repeats must be positive")
    if args.repeat_start < 0:
        raise ValueError("repeat_start must be non-negative")

    rows = []
    for repeat in range(args.repeat_start, args.repeat_start + args.repeats):
        for fold in folds:
            config = json.loads(json.dumps(base))
            config["seed"] = int(base["seed"]) + repeat * int(args.seed_stride)
            config["test_fold"] = fold
            config["validation_fold"] = (fold + 1) % n_folds
            run_name = f"{args.experiment_name}_r{repeat:02d}_f{fold:02d}"
            run_dir = run_training(config, run_name)
            rows.append(_run_row(run_dir, repeat, fold, config["seed"]))

    frame = pd.DataFrame(rows)
    summary_dir = Path(base["runs_dir"]) / "cv_summaries" / args.experiment_name
    summary_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(summary_dir / "fold_metrics.csv", index=False, encoding="utf-8-sig")
    payload = {
        "experiment_name": args.experiment_name,
        "config_file": str(args.config.resolve()),
        "config": base,
        "repeats": args.repeats,
        "repeat_start": args.repeat_start,
        "folds": folds,
        "aggregate": _aggregate(frame),
    }
    (summary_dir / "summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(summary_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
