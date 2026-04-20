"""CyanoHABs 预测模型 — 训练入口脚本。"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
from rich.table import Table

from src.config import CLEANED_DIR, DATASET_REGISTRY, FIGURE_DIR, MODEL_DIR
from src.features import build_feature_matrix_for
from src.logger import console, log_error, log_info, log_success, log_warning
from src.train import (
    cross_validate,
    save_models,
    split_data,
    train_ensemble,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CyanoHABs 预测模型训练")
    parser.add_argument(
        "--dataset",
        choices=list(DATASET_REGISTRY.keys()),
        default="habs_training",
        help="数据集名称",
    )
    parser.add_argument(
        "--task",
        choices=["classification", "regression", "both"],
        default="both",
        help="训练任务类型",
    )
    parser.add_argument(
        "--tune",
        action="store_true",
        help="启用 Optuna 超参搜索",
    )
    parser.add_argument("--n-trials", type=int, default=50, help="Optuna 搜索次数")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument(
        "--cv",
        type=int,
        default=5,
        help="交叉验证折数",
    )
    return parser.parse_args()


def _print_data_summary(df: pd.DataFrame, dataset: str) -> None:
    """打印数据摘要表格。"""
    cfg = DATASET_REGISTRY[dataset]
    table = Table(title=f"{dataset} 数据概览")
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")
    rows = [
        ("总行数", f"{len(df):,}"),
        ("总列数", f"{len(df.columns)}"),
        ("数据集", dataset),
    ]
    date_col = cfg.get("date_col")
    if date_col and date_col in df.columns:
        dt = pd.to_datetime(df[date_col], errors="coerce")
        rows.append(("时间范围", f"{dt.min():%Y-%m} ~ {dt.max():%Y-%m}"))
    for attr, val in rows:
        table.add_row(attr, val)
    console.print(table)


def _print_metrics_table(
    results: dict[str, dict],
    task: str,
) -> None:
    """打印模型对比表格。"""
    table = Table(title=f"{task} 模型对比")
    table.add_column("模型", style="cyan")

    all_metrics: list[str] = []
    for metrics in results.values():
        for k in metrics:
            if k not in all_metrics and k != "optimal_threshold":
                all_metrics.append(k)
    for m in all_metrics:
        table.add_column(m)

    for model_name, metrics in results.items():
        row = [model_name]
        for m in all_metrics:
            val = metrics.get(m, float("nan"))
            row.append(f"{val:.4f}" if isinstance(val, float) else str(val))
        table.add_row(*row)
    console.print(table)


def run_task(
    df: pd.DataFrame,
    dataset: str,
    task: str,
    seed: int,
    n_cv: int,
    figure_dir: Path,
) -> dict[str, dict]:
    """运行单个任务（分类或回归）的完整流程。"""
    log_info(f"{'='*20} {task.upper()} {'='*20}")

    small = len(df) < 500

    # 特征工程
    X, y, feature_names = build_feature_matrix_for(df, dataset=dataset, task=task)

    # 训练/测试划分
    X_train, X_test, y_train, y_test = split_data(
        X, y, df_source=df if dataset == "habs_training" else None,
        task=task, seed=seed,
    )
    log_info(f"训练集: {len(X_train)} 行, 测试集: {len(X_test)} 行")

    # 训练集成模型
    models, val_pred_ensemble = train_ensemble(
        X_train, y_train, X_test, y_test, task, small=small,
    )

    # 各模型单独评估
    from src.evaluate import evaluate_full_pipeline

    results: dict[str, dict] = {}
    for i, model in enumerate(models):
        model_name = "XGBoost" if i == 0 else "LightGBM"
        if task == "classification":
            pred = model.predict_proba(X_test)[:, 1]
        else:
            pred = model.predict(X_test)
        metrics = evaluate_full_pipeline(
            y_test, pred, pred, task, model_name, figure_dir,
        )
        results[model_name] = metrics

    # 集成评估
    metrics_ens = evaluate_full_pipeline(
        y_test, val_pred_ensemble, val_pred_ensemble, task, "Ensemble", figure_dir,
    )
    results["Ensemble"] = metrics_ens

    _print_metrics_table(results, task)

    # 交叉验证
    cv_results = cross_validate(X, y, task, n_splits=n_cv, seed=seed)
    log_info(f"CV 平均指标 ({task}):")
    metric_keys = [k for k in cv_results[0] if k != "fold"]
    for key in metric_keys:
        vals = [r[key] for r in cv_results]
        mean_val = sum(vals) / len(vals)
        log_info(f"  {key}: {mean_val:.4f}")

    # 保存模型
    save_models(models, task, feature_names, dataset=dataset)

    return results


def main() -> None:
    args = parse_args()
    start_time = time.time()

    dataset = args.dataset
    cfg = DATASET_REGISTRY[dataset]

    log_info(f"CyanoHABs 预测模型训练 [{dataset}]")

    # 图表/模型输出目录
    if dataset == "habs_training":
        fig_dir = FIGURE_DIR
    else:
        fig_dir = FIGURE_DIR / dataset
    fig_dir.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # 加载数据
    data_path = CLEANED_DIR / cfg["path"]
    if not data_path.exists():
        log_error(f"数据文件不存在: {data_path}")
        return
    df = pd.read_parquet(data_path)
    log_success(f"数据加载完成: {len(df)} 行 × {len(df.columns)} 列")
    _print_data_summary(df, dataset)

    all_results: dict[str, dict[str, dict]] = {}

    # 分类任务
    if args.task in ("classification", "both"):
        all_results["classification"] = run_task(
            df, dataset, "classification", args.seed, args.cv, fig_dir,
        )

    # 回归任务
    if args.task in ("regression", "both"):
        all_results["regression"] = run_task(
            df, dataset, "regression", args.seed, args.cv, fig_dir,
        )

    # SHAP 解释
    try:
        from src.interpret import interpret_model
        from src.train import load_models

        for task_name in all_results:
            log_info(f"生成 {task_name} SHAP 解释...")
            saved = load_models(task_name, dataset=dataset)
            X, y, _ = build_feature_matrix_for(df, dataset=dataset, task=task_name)
            interpret_model(
                saved["models"][0], X, y, task_name, fig_dir / "shap",
            )
    except Exception as e:
        log_warning(f"SHAP 解释生成失败: {e}")

    elapsed = time.time() - start_time
    log_success(f"全流程完成，耗时 {elapsed:.1f}s")
    log_info(f"图表保存至: {fig_dir}")
    log_info(f"模型保存至: {MODEL_DIR}")


if __name__ == "__main__":
    main()
