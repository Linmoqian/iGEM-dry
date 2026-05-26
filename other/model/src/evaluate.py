"""模型评估与可视化模块：分类/回归指标计算、阈值优化、诊断图表。"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    r2_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
)

from src.config import FIGURE_DIR
from src.logger import log_error, log_info, log_success

# matplotlib 全局配置
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150


# ---------------------------------------------------------------------------
# 指标计算
# ---------------------------------------------------------------------------

def compute_classification_metrics(
    y_true: np.ndarray | pd.Series,
    y_pred_proba: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    """计算二分类评估指标。

    Parameters
    ----------
    y_true : 真实标签 (0/1)
    y_pred_proba : 正类预测概率
    threshold : 二值化阈值

    Returns
    -------
    包含 ROC-AUC, PR-AUC, Accuracy, Balanced Accuracy, F1, MCC,
    Precision, Recall 的扁平字典
    """
    y_true = np.asarray(y_true)
    y_pred_proba = np.asarray(y_pred_proba)
    y_pred_binary = (y_pred_proba >= threshold).astype(int)

    metrics: dict[str, float] = {
        "roc_auc": roc_auc_score(y_true, y_pred_proba),
        "pr_auc": average_precision_score(y_true, y_pred_proba),
        "accuracy": accuracy_score(y_true, y_pred_binary),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred_binary),
        "f1": f1_score(y_true, y_pred_binary, zero_division=0),
        "mcc": matthews_corrcoef(y_true, y_pred_binary),
        "precision": precision_score(y_true, y_pred_binary, zero_division=0),
        "recall": recall_score(y_true, y_pred_binary, zero_division=0),
    }
    return metrics


def compute_regression_metrics(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray,
) -> dict[str, float]:
    """计算回归评估指标 (目标为 log10(MICX))。

    Parameters
    ----------
    y_true : 真实 log10(MICX)
    y_pred : 预测 log10(MICX)

    Returns
    -------
    包含 RMSE(log), RMSE(orig), MAE(orig), R2, Pearson r, Spearman rho,
    within_factor_of_2 的扁平字典
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    # log 尺度指标
    rmse_log = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))

    # 原始尺度回变换
    actual_orig = np.power(10, y_true)
    pred_orig = np.power(10, y_pred)
    rmse_orig = float(np.sqrt(mean_squared_error(actual_orig, pred_orig)))
    mae_orig = float(mean_absolute_error(actual_orig, pred_orig))

    # 相关性
    pearson_r = float(stats.pearsonr(y_true, y_pred)[0])
    spearman_rho = float(stats.spearmanr(y_true, y_pred)[0])

    # within-factor-of-2
    ratio = pred_orig / actual_orig
    within_f2 = float(np.mean((ratio >= 0.5) & (ratio <= 2.0)) * 100)

    metrics: dict[str, float] = {
        "rmse_log": rmse_log,
        "rmse_orig": rmse_orig,
        "mae_orig": mae_orig,
        "r2": r2,
        "pearson_r": pearson_r,
        "spearman_rho": spearman_rho,
        "within_factor_of_2": within_f2,
    }
    return metrics


# ---------------------------------------------------------------------------
# 阈值优化
# ---------------------------------------------------------------------------

def find_optimal_threshold(
    y_true: np.ndarray | pd.Series,
    y_pred_proba: np.ndarray,
) -> float:
    """通过最大化 F1 分数寻找最优分类阈值。

    扫描 0.1 ~ 0.9, 步长 0.01。

    Returns
    -------
    最优阈值 (float)
    """
    y_true = np.asarray(y_true)
    y_pred_proba = np.asarray(y_pred_proba)

    best_threshold = 0.5
    best_f1 = 0.0

    for threshold in np.arange(0.1, 0.91, 0.01):
        y_pred_binary = (y_pred_proba >= threshold).astype(int)
        f1 = f1_score(y_true, y_pred_binary, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)

    log_info(f"最优阈值: {best_threshold:.2f} (F1={best_f1:.4f})")
    return best_threshold


# ---------------------------------------------------------------------------
# 可视化
# ---------------------------------------------------------------------------

def plot_target_distribution(
    y_clf: np.ndarray | pd.Series,
    y_reg: np.ndarray | pd.Series,
    save_dir: Path,
) -> None:
    """绘制目标变量分布图。

    左: MICX_DET 二分类分布 (柱状图)
    右: log10(MICX) 分布 (直方图 + KDE)
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 左: 分类目标
    counts = np.bincount(np.asarray(y_clf).astype(int))
    labels = ["Negative (0)", "Positive (1)"]
    bars = axes[0].bar(labels, counts, color=["#4C72B0", "#DD8452"], edgecolor="white")
    for bar, count in zip(bars, counts):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(counts) * 0.02,
            str(count),
            ha="center",
            va="bottom",
            fontsize=11,
        )
    axes[0].set_title("MICX_DET 分布", fontsize=13)
    axes[0].set_ylabel("样本数")

    # 右: 回归目标
    y_reg_arr = np.asarray(y_reg)
    sns.histplot(y_reg_arr, kde=True, ax=axes[1], color="#4C72B0", edgecolor="white")
    axes[1].set_title("log10(MICX) 分布", fontsize=13)
    axes[1].set_xlabel("log10(MICX)")
    axes[1].set_ylabel("频数")

    plt.tight_layout()
    save_path = save_dir / "target_distribution.webp"
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"目标分布图已保存: {save_path}")


def plot_confusion_matrix(
    y_true: np.ndarray | pd.Series,
    y_pred_binary: np.ndarray,
    labels: list[str] | None = None,
    save_path: Path | None = None,
) -> None:
    """绘制混淆矩阵热力图。

    单元格标注数量和百分比, 蓝色配色。
    """
    if save_path is None:
        save_path = FIGURE_DIR / "confusion_matrix.webp"
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if labels is None:
        labels = ["Negative (0)", "Positive (1)"]

    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred_binary)
    cm = confusion_matrix(y_true_arr, y_pred_arr)
    total = cm.sum()

    # 构建标注: 数量 + 百分比
    annot = np.empty_like(cm, dtype=object)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            pct = cm[i, j] / total * 100 if total > 0 else 0
            annot[i, j] = f"{cm[i, j]}\n({pct:.1f}%)"

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(
        cm,
        annot=annot,
        fmt="",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
    )
    ax.set_xlabel("预测标签", fontsize=12)
    ax.set_ylabel("真实标签", fontsize=12)
    ax.set_title("混淆矩阵", fontsize=13)

    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"混淆矩阵已保存: {save_path}")


def plot_roc_pr_curves(
    y_true: np.ndarray | pd.Series,
    y_pred_proba: np.ndarray,
    save_dir: Path,
) -> None:
    """绘制 ROC 曲线和 PR 曲线 (左右子图)。

    分别保存为 roc_curve.webp 和 pr_curve.webp (在同一 figure 中)。
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    y_true_arr = np.asarray(y_true)
    y_pred_proba_arr = np.asarray(y_pred_proba)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ROC 曲线
    fpr, tpr, _ = roc_curve(y_true_arr, y_pred_proba_arr)
    roc_auc = roc_auc_score(y_true_arr, y_pred_proba_arr)
    axes[0].plot(fpr, tpr, color="#4C72B0", lw=2, label=f"AUC = {roc_auc:.4f}")
    axes[0].plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
    axes[0].set_xlabel("假阳性率 (FPR)", fontsize=11)
    axes[0].set_ylabel("真阳性率 (TPR)", fontsize=11)
    axes[0].set_title("ROC 曲线", fontsize=13)
    axes[0].legend(loc="lower right", fontsize=11)
    axes[0].set_xlim([0, 1])
    axes[0].set_ylim([0, 1.05])

    # PR 曲线
    precision_vals, recall_vals, _ = precision_recall_curve(y_true_arr, y_pred_proba_arr)
    ap = average_precision_score(y_true_arr, y_pred_proba_arr)
    axes[1].plot(recall_vals, precision_vals, color="#DD8452", lw=2, label=f"AP = {ap:.4f}")
    axes[1].set_xlabel("召回率 (Recall)", fontsize=11)
    axes[1].set_ylabel("精确率 (Precision)", fontsize=11)
    axes[1].set_title("PR 曲线", fontsize=13)
    axes[1].legend(loc="upper right", fontsize=11)
    axes[1].set_xlim([0, 1])
    axes[1].set_ylim([0, 1.05])

    plt.tight_layout()
    save_path = save_dir / "roc_pr_curves.webp"
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"ROC/PR 曲线已保存: {save_path}")


def plot_predicted_vs_actual(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray,
    save_path: Path | None = None,
) -> None:
    """回归: 预测值 vs 真实值散点图 (log 尺度)。

    对角参考线, 按误差大小着色, 标注 RMSE/R2/Pearson r。
    """
    if save_path is None:
        save_path = FIGURE_DIR / "predicted_vs_actual.webp"
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    errors = np.abs(y_true_arr - y_pred_arr)

    metrics = compute_regression_metrics(y_true_arr, y_pred_arr)

    fig, ax = plt.subplots(figsize=(8, 8))
    scatter = ax.scatter(
        y_true_arr,
        y_pred_arr,
        c=errors,
        cmap="RdYlGn_r",
        alpha=0.6,
        edgecolors="grey",
        linewidths=0.5,
        s=40,
    )
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.8)
    cbar.set_label("绝对误差 (log 尺度)", fontsize=10)

    # 对角参考线
    lims = [
        min(y_true_arr.min(), y_pred_arr.min()),
        max(y_true_arr.max(), y_pred_arr.max()),
    ]
    ax.plot(lims, lims, "k--", lw=1, alpha=0.7, label="y = x")

    ax.set_xlabel("真实值 log10(MICX)", fontsize=12)
    ax.set_ylabel("预测值 log10(MICX)", fontsize=12)
    ax.set_title("预测值 vs 真实值", fontsize=13)

    textstr = (
        f"RMSE(log) = {metrics['rmse_log']:.4f}\n"
        f"R2 = {metrics['r2']:.4f}\n"
        f"Pearson r = {metrics['pearson_r']:.4f}"
    )
    ax.text(
        0.05,
        0.95,
        textstr,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
    )
    ax.legend(loc="lower right")

    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"预测 vs 真实散点图已保存: {save_path}")


def plot_residuals(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray,
    save_path: Path | None = None,
) -> None:
    """回归: 残差分布直方图 + KDE。"""
    if save_path is None:
        save_path = FIGURE_DIR / "residuals.webp"
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    residuals = y_true_arr - y_pred_arr

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(residuals, kde=True, ax=ax, color="#4C72B0", edgecolor="white")
    ax.axvline(x=0, color="red", linestyle="--", lw=1, alpha=0.7)
    ax.set_xlabel("残差 (真实 - 预测)", fontsize=12)
    ax.set_ylabel("频数", fontsize=12)
    ax.set_title("残差分布", fontsize=13)

    textstr = (
        f"Mean = {residuals.mean():.4f}\n"
        f"Std = {residuals.std():.4f}"
    )
    ax.text(
        0.95,
        0.95,
        textstr,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        horizontalalignment="right",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
    )

    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"残差分布图已保存: {save_path}")


def plot_model_comparison(
    results: dict[str, dict],
    task: str,
    save_path: Path | None = None,
) -> None:
    """模型对比柱状图。

    Parameters
    ----------
    results : {model_name: {metric_name: value, ...}, ...}
    task : "classification" 或 "regression"
    save_path : 保存路径
    """
    if save_path is None:
        save_path = FIGURE_DIR / "model_comparison.webp"
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if task == "classification":
        metric_keys = ["roc_auc", "f1", "mcc"]
        metric_labels = ["ROC-AUC", "F1", "MCC"]
    else:
        metric_keys = ["rmse_log", "r2", "mae_orig"]
        metric_labels = ["RMSE (log)", "R2", "MAE (orig)"]

    model_names = list(results.keys())
    n_models = len(model_names)
    n_metrics = len(metric_keys)

    x = np.arange(n_metrics)
    width = 0.8 / max(n_models, 1)
    colors = ["#4C72B0", "#DD8452", "#55A868"]

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, name in enumerate(model_names):
        values = [results[name].get(k, 0.0) for k in metric_keys]
        offset = (i - (n_models - 1) / 2) * width
        bars = ax.bar(
            x + offset,
            values,
            width=width,
            label=name,
            color=colors[i % len(colors)],
            edgecolor="white",
        )
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005,
                f"{val:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, fontsize=11)
    ax.set_ylabel("指标值", fontsize=12)
    ax.set_title("模型性能对比", fontsize=13)
    ax.legend(fontsize=10)

    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log_success(f"模型对比图已保存: {save_path}")


# ---------------------------------------------------------------------------
# 主评估入口
# ---------------------------------------------------------------------------

def evaluate_full_pipeline(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray,
    y_pred_proba: np.ndarray | None,
    task: str,
    model_name: str,
    save_dir: Path | None = None,
) -> dict[str, float]:
    """运行完整评估流程, 生成所有图表并返回指标字典。

    Parameters
    ----------
    y_true : 真实值
    y_pred : 分类时为二值预测, 回归时为连续预测
    y_pred_proba : 分类时的正类概率 (回归时可为 None)
    task : "classification" 或 "regression"
    model_name : 模型名称 (用于文件命名)
    save_dir : 图表保存目录, 默认 FIGURE_DIR

    Returns
    -------
    评估指标字典
    """
    if save_dir is None:
        save_dir = FIGURE_DIR
    save_dir = Path(save_dir)
    model_dir = save_dir / model_name
    model_dir.mkdir(parents=True, exist_ok=True)

    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)

    log_info(f"评估 {model_name} ({task}): {len(y_true_arr)} 样本")

    if task == "classification":
        if y_pred_proba is None:
            log_error("分类任务需要 y_pred_proba")
            msg = "y_pred_proba is required for classification task"
            raise ValueError(msg)
        y_pred_proba_arr = np.asarray(y_pred_proba)

        metrics = compute_classification_metrics(y_true_arr, y_pred_proba_arr)
        log_info(
            "分类指标: "
            + "  ".join(f"{k}={v:.4f}" for k, v in metrics.items())
        )

        # 混淆矩阵
        y_pred_binary = (y_pred_proba_arr >= 0.5).astype(int)
        plot_confusion_matrix(
            y_true_arr,
            y_pred_binary,
            save_path=model_dir / "confusion_matrix.webp",
        )

        # ROC / PR 曲线
        plot_roc_pr_curves(y_true_arr, y_pred_proba_arr, save_dir=model_dir)

    elif task == "regression":
        metrics = compute_regression_metrics(y_true_arr, y_pred_arr)
        log_info(
            "回归指标: "
            + "  ".join(f"{k}={v:.4f}" for k, v in metrics.items())
        )

        # 预测 vs 真实
        plot_predicted_vs_actual(
            y_true_arr,
            y_pred_arr,
            save_path=model_dir / "predicted_vs_actual.webp",
        )

        # 残差分布
        plot_residuals(
            y_true_arr,
            y_pred_arr,
            save_path=model_dir / "residuals.webp",
        )

    else:
        msg = f"未知任务类型: {task}"
        raise ValueError(msg)

    log_success(f"{model_name} ({task}) 评估完成")
    return metrics
