"""SHAP 模型解释模块：特征重要性分析、依赖图、瀑布图、多方法对比。"""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from sklearn.inspection import permutation_importance

from src.config import FIGURE_DIR
from src.logger import log_error, log_info, log_success, log_warning

plt.style.use("seaborn-v0_8-whitegrid")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


def _ensure_dir(path: Path) -> Path:
    """确保目录存在，返回该路径。"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_model_booster(model):
    """从 sklearn-wrapper 模型中提取底层 booster (LightGBM 需要)。"""
    if hasattr(model, "booster_"):
        return model.booster_
    return model


def compute_shap_values(model, X: pd.DataFrame) -> shap.Explanation:
    """计算 SHAP 值，支持 XGBoost 和 LightGBM。"""
    log_info("正在计算 SHAP 值...")
    start = time.perf_counter()

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)

    elapsed = time.perf_counter() - start
    log_success(f"SHAP 值计算完成, 耗时 {elapsed:.2f}s")
    return shap_values


def plot_shap_beeswarm(
    shap_values: shap.Explanation,
    feature_names: list[str],
    save_path: Path,
) -> None:
    """SHAP 蜂群图：全局特征重要性分布。"""
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.plots.beeswarm(shap_values, max_display=20, show=False)
    ax.set_title("SHAP 特征重要性分布", fontsize=14, fontweight="bold")

    plt.tight_layout()
    _ensure_dir(save_path.parent)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"蜂群图已保存: {save_path}")


def plot_shap_bar(
    shap_values: shap.Explanation,
    feature_names: list[str],
    save_path: Path,
) -> None:
    """SHAP 柱状图：平均绝对 SHAP 值排名。"""
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.plots.bar(shap_values, max_display=20, show=False)
    ax.set_title("SHAP 平均绝对重要性", fontsize=14, fontweight="bold")

    plt.tight_layout()
    _ensure_dir(save_path.parent)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"柱状图已保存: {save_path}")


def plot_shap_dependence(
    shap_values: shap.Explanation,
    X: pd.DataFrame,
    top_n: int = 5,
    save_dir: Path | None = None,
) -> None:
    """SHAP 依赖图：前 N 个最重要特征的单特征效应。"""
    if save_dir is None:
        save_dir = FIGURE_DIR / "shap_dependence"
    _ensure_dir(save_dir)

    mean_abs = np.abs(shap_values.values).mean(axis=0)
    top_indices = np.argsort(mean_abs)[::-1][:top_n]
    feature_names = list(X.columns)

    for rank, idx in enumerate(top_indices):
        fname = feature_names[idx]
        fig, ax = plt.subplots(figsize=(8, 6))

        shap.dependence_plot(
            idx,
            shap_values.values,
            X,
            ax=ax,
            show=False,
        )
        ax.set_title(f"SHAP 依赖图: {fname}", fontsize=13, fontweight="bold")
        ax.set_xlabel(fname, fontsize=11)
        ax.set_ylabel(f"SHAP value ({fname})", fontsize=11)

        plt.tight_layout()
        safe_name = fname.replace("/", "_").replace("\\", "_").replace(" ", "_")
        out_path = save_dir / f"shap_dependence_{safe_name}.webp"
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        log_info(f"依赖图 ({rank + 1}/{top_n}): {fname} -> {out_path}")

    log_success(f"依赖图全部保存完成 ({top_n} 个特征)")


def plot_shap_waterfall(
    shap_values: shap.Explanation,
    X: pd.DataFrame,
    indices: list[int],
    save_dir: Path | None = None,
) -> None:
    """SHAP 瀑布图：指定样本的预测解释。"""
    if save_dir is None:
        save_dir = FIGURE_DIR / "shap_waterfall"
    _ensure_dir(save_dir)

    for idx in indices:
        if idx < 0 or idx >= len(X):
            log_warning(f"样本索引 {idx} 超出范围, 跳过")
            continue

        fig, ax = plt.subplots(figsize=(10, 8))

        shap.plots.waterfall(shap_values[idx], max_display=15, show=False)

        pred_val = shap_values[idx].values.sum() + shap_values.base_values[idx]
        ax.set_title(
            f"SHAP 瀑布图 (样本 {idx}, 预测值={pred_val:.4f})",
            fontsize=13,
            fontweight="bold",
        )

        plt.tight_layout()
        out_path = save_dir / f"shap_waterfall_{idx}.webp"
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        log_info(f"瀑布图 (样本 {idx}): {out_path}")

    log_success(f"瀑布图全部保存完成 ({len(indices)} 个样本)")


def plot_feature_importance_comparison(
    models: list,
    feature_names: list[str],
    X: pd.DataFrame,
    y: pd.Series,
    save_path: Path,
) -> None:
    """多方法特征重要性对比：内置 gain / SHAP / 置换重要性。"""
    importance_dicts: dict[str, dict[str, float]] = {}

    # 内置 gain 重要性
    for model in models:
        model_type = type(model).__name__
        if hasattr(model, "feature_importances_"):
            importance_dicts[f"{model_type} Gain"] = dict(
                zip(feature_names, model.feature_importances_)
            )

    # SHAP 重要性
    shap_explainer = shap.TreeExplainer(models[0])
    shap_vals = shap_explainer.shap_values(X)

    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]

    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    importance_dicts["SHAP"] = dict(zip(feature_names, mean_abs_shap))

    # 置换重要性
    from sklearn.metrics import make_scorer, r2_score, roc_auc_score

    if hasattr(models[0], "predict_proba"):
        scoring = "roc_auc"
    else:
        scoring = "r2"

    perm_result = permutation_importance(
        models[0], X, y, n_repeats=10, random_state=42, scoring=scoring, n_jobs=-1,
    )
    importance_dicts["Permutation"] = dict(
        zip(feature_names, perm_result.importances_mean)
    )

    # 汇总并取 top 15
    all_features = pd.DataFrame(importance_dicts)
    all_features = all_features.fillna(0)

    # 归一化每种方法到 [0, 1] 以便横向对比
    for col in all_features.columns:
        col_max = all_features[col].max()
        if col_max > 0:
            all_features[col] = all_features[col] / col_max

    mean_rank = all_features.mean(axis=1).sort_values(ascending=False)
    top_features = mean_rank.head(15).index.tolist()

    plot_df = all_features.loc[top_features]

    # 横向柱状图
    n_methods = len(plot_df.columns)
    fig, axes = plt.subplots(1, n_methods, figsize=(6 * n_methods, 8), sharey=True)
    if n_methods == 1:
        axes = [axes]

    for ax, method_name in zip(axes, plot_df.columns):
        values = plot_df[method_name].values
        bars = ax.barh(range(len(top_features)), values, color=sns.color_palette("viridis", len(top_features)))
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel("Normalized Importance", fontsize=10)
        ax.set_title(method_name, fontsize=12, fontweight="bold")

    fig.suptitle("特征重要性多方法对比 (Top 15)", fontsize=14, fontweight="bold")
    plt.tight_layout()

    _ensure_dir(save_path.parent)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"重要性对比图已保存: {save_path}")


def interpret_model(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    task: str,
    save_dir: Path | None = None,
) -> dict:
    """主函数：运行完整 SHAP 解释流程。

    1. 计算 SHAP 值
    2. 生成蜂群图 + 柱状图
    3. 生成前 5 个特征的依赖图
    4. 生成 3 个瀑布图 (高/中/低预测值样本)
    5. 返回 top 10 特征及其平均绝对 SHAP 值

    Parameters
    ----------
    model : 训练好的 XGBoost 或 LightGBM 模型
    X : 特征 DataFrame
    y : 目标变量
    task : "classification" 或 "regression"
    save_dir : 图表保存目录, 默认 FIGURE_DIR / "interpretation"

    Returns
    -------
    dict : {"top_features": [(feature_name, mean_abs_shap), ...]}
    """
    if save_dir is None:
        save_dir = FIGURE_DIR / "shap"
    _ensure_dir(save_dir)

    log_info(f"开始模型解释 ({task}), 特征数={X.shape[1]}, 样本数={X.shape[0]}")

    # 1. 计算 SHAP 值
    shap_values = compute_shap_values(model, X)

    # 2. 蜂群图 + 柱状图
    plot_shap_beeswarm(
        shap_values,
        feature_names=list(X.columns),
        save_path=save_dir / "shap_beeswarm.webp",
    )
    plot_shap_bar(
        shap_values,
        feature_names=list(X.columns),
        save_path=save_dir / "shap_bar.webp",
    )

    # 3. 依赖图
    plot_shap_dependence(
        shap_values,
        X,
        top_n=5,
        save_dir=save_dir / "dependence",
    )

    # 4. 瀑布图: 选取高/中/低预测值样本
    preds = shap_values.values.sum(axis=1) + shap_values.base_values
    sorted_idx = np.argsort(preds)
    n_samples = len(preds)
    indices = [
        int(sorted_idx[-1]),   # 最高预测值
        int(sorted_idx[n_samples // 2]),  # 中位数
        int(sorted_idx[0]),    # 最低预测值
    ]
    plot_shap_waterfall(
        shap_values,
        X,
        indices=indices,
        save_dir=save_dir / "waterfall",
    )

    # 5. 汇总 top 10 特征
    mean_abs = np.abs(shap_values.values).mean(axis=0)
    top_indices = np.argsort(mean_abs)[::-1][:10]
    feature_names = list(X.columns)
    top_features = [
        (feature_names[i], float(mean_abs[i]))
        for i in top_indices
    ]

    log_success("模型解释完成")
    for rank, (fname, val) in enumerate(top_features, start=1):
        log_info(f"  {rank:>2}. {fname:<30s} mean|SHAP| = {val:.6f}")

    return {"top_features": top_features}
