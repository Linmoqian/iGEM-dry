"""Command-line interface for local validation and server training."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import logging
import sys
from pathlib import Path

from .config import load_config
from .data import dataset_summary, load_dataset
from .inference import predict_from_run
from .models.factory import SUPPORTED_MODELS
from .pipeline import run_training
from .splits import make_split_manifest, split_summary, write_split_artifacts


def _common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, help="JSON config merged over configs/default.json")
    parser.add_argument("--target", choices=["total_microcystins", "mc_lr"])
    parser.add_argument("--panel", choices=["core_field", "static_context", "bloom_augmented", "hybrid"])
    parser.add_argument("--split-protocol", choices=["source_ood", "waterbody_ood", "temporal_ood"])
    parser.add_argument("--n-folds", type=int)
    parser.add_argument("--test-fold", type=int)
    parser.add_argument("--validation-fold", type=int)


def _overrides(args) -> dict:
    result = {}
    for argument, key in [
        (args.target, "target"),
        (args.panel, "panel"),
        (args.split_protocol, "split_protocol"),
        (args.n_folds, "n_folds"),
        (args.test_fold, "test_fold"),
        (args.validation_fold, "validation_fold"),
    ]:
        if argument is not None:
            result[key] = argument
    return result


def _smoke_config(config: dict) -> None:
    config["stacking_folds"] = 2
    config["xgb_aft"].update({"num_boost_round": 25, "early_stopping_rounds": 5, "max_depth": 3})
    config["catboost_quantile"].update({"iterations": 25, "early_stopping_rounds": 5, "depth": 4})
    config["lightgbm_quantile"].update({"n_estimators": 30, "early_stopping_rounds": 5, "num_leaves": 15})
    config["tabm_censored"].update(
        {
            "ensemble_size": 4,
            "hidden_dims": [64, 32],
            "batch_size": 1024,
            "max_epochs": 3,
            "patience": 2,
        }
    )
    config["tabicl"].update({"n_estimators": 2, "batch_size": 2})


def _inspect_environment() -> int:
    packages = [
        "numpy",
        "pandas",
        "scipy",
        "scikit-learn",
        "pyarrow",
        "xgboost",
        "lightgbm",
        "catboost",
        "torch",
        "tabicl",
    ]
    rows = {}
    for package in packages:
        try:
            rows[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            rows[package] = None
    print(json.dumps({"python": sys.version, "packages": rows}, indent=2))
    required = [name for name in packages if name != "tabicl"]
    return 0 if all(rows[name] is not None for name in required) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmadre", description="CMADRE microcystin modeling pipeline")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate-data", help="load data, validate labels/features, print summary"
    )
    _common_arguments(validate)

    split = subparsers.add_parser("make-splits", help="create and validate a split manifest")
    _common_arguments(split)
    split.add_argument("--output", type=Path, default=Path("runs/split_preview"))

    train = subparsers.add_parser("train", help="train, stack, calibrate, and evaluate models")
    _common_arguments(train)
    train.add_argument("--models", help=f"comma-separated subset of: {','.join(sorted(SUPPORTED_MODELS))}")
    train.add_argument("--stacking-folds", type=int)
    train.add_argument("--risk-thresholds", help="comma-separated µg/L values; empty by default")
    train.add_argument("--run-name")
    train.add_argument(
        "--smoke", action="store_true", help="small iteration counts; validates code, not performance"
    )

    subparsers.add_parser(
        "inspect-env", help="print dependency versions and return non-zero if core packages are missing"
    )
    predict = subparsers.add_parser("predict", help="reload a completed run and predict CSV/Parquet rows")
    predict.add_argument("--run-dir", type=Path, required=True)
    predict.add_argument("--input", type=Path, required=True)
    predict.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    if args.command == "inspect-env":
        return _inspect_environment()
    if args.command == "predict":
        output = predict_from_run(args.run_dir, args.input, args.output)
        print(str(output))
        return 0

    config = load_config(args.config, _overrides(args))
    if args.command == "validate-data":
        print(json.dumps(dataset_summary(load_dataset(config)), ensure_ascii=False, indent=2))
        return 0
    if args.command == "make-splits":
        data = load_dataset(config)
        manifest = make_split_manifest(data, config)
        output = args.output.expanduser().resolve()
        write_split_artifacts(manifest, output)
        print(json.dumps({"output": str(output), **split_summary(manifest)}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "train":
        if args.models:
            models = [name.strip() for name in args.models.split(",") if name.strip()]
            unknown = set(models) - SUPPORTED_MODELS
            if unknown:
                parser.error(f"unknown models: {sorted(unknown)}")
            config["models"] = models
        if args.stacking_folds is not None:
            config["stacking_folds"] = args.stacking_folds
        if args.risk_thresholds is not None:
            config["risk_thresholds_ug_l"] = [
                float(value) for value in args.risk_thresholds.split(",") if value.strip()
            ]
        if args.smoke:
            _smoke_config(config)
        run_dir = run_training(config, args.run_name)
        print(str(run_dir))
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
