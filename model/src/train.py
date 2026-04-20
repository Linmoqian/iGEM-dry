"""模型训练模块：XGBoost/LightGBM 分类+回归训练、集成、超参调优。"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, train_test_split

from src.config import MODEL_DIR
from src.logger import log_info, log_success


def get_default_params(task: str, model_type: str, small: bool = False) -> dict:
    """返回合理的默认超参数。small=True 用于小数据集（<500 行）。"""
    if small:
        return _get_small_params(task, model_type)
    if task == "classification":
        if model_type == "xgboost":
            return {
                "n_estimators": 500,
                "max_depth": 5,
                "learning_rate": 0.05,
                "min_child_weight": 5,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "reg_alpha": 0.1,
                "reg_lambda": 1.0,
                "scale_pos_weight": 1.95,
                "early_stopping_rounds": 50,
                "eval_metric": "logloss",
                "verbosity": 0,
                "n_jobs": -1,
                "random_state": 42,
            }
        return {
            "n_estimators": 500,
            "max_depth": 5,
            "num_leaves": 31,
            "learning_rate": 0.05,
            "min_child_samples": 20,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "is_unbalance": True,
            "verbosity": -1,
            "n_jobs": -1,
            "random_state": 42,
        }
    # regression
    if model_type == "xgboost":
        return {
            "n_estimators": 500,
            "max_depth": 5,
            "learning_rate": 0.05,
            "min_child_weight": 5,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "early_stopping_rounds": 50,
            "objective": "reg:squarederror",
            "verbosity": 0,
            "n_jobs": -1,
            "random_state": 42,
        }
    return {
        "n_estimators": 500,
        "max_depth": 5,
        "num_leaves": 31,
        "learning_rate": 0.05,
        "min_child_samples": 10,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "objective": "regression",
        "verbosity": -1,
        "n_jobs": -1,
        "random_state": 42,
    }


def _create_model(task: str, model_type: str, params: dict):
    """创建模型实例。"""
    if model_type == "xgboost":
        return xgb.XGBClassifier(**params) if task == "classification" else xgb.XGBRegressor(**params)
    return lgb.LGBMClassifier(**params) if task == "classification" else lgb.LGBMRegressor(**params)


def _get_small_params(task: str, model_type: str) -> dict:
    """小数据集（<500 行）的保守参数，防止过拟合。"""
    if task == "classification":
        if model_type == "xgboost":
            return {
                "n_estimators": 300,
                "max_depth": 3,
                "learning_rate": 0.05,
                "min_child_weight": 10,
                "subsample": 0.8,
                "colsample_bytree": 0.7,
                "reg_alpha": 1.0,
                "reg_lambda": 5.0,
                "scale_pos_weight": 1.8,
                "early_stopping_rounds": 30,
                "eval_metric": "logloss",
                "verbosity": 0,
                "n_jobs": -1,
                "random_state": 42,
            }
        return {
            "n_estimators": 300,
            "max_depth": 3,
            "num_leaves": 15,
            "learning_rate": 0.05,
            "min_child_samples": 15,
            "subsample": 0.8,
            "colsample_bytree": 0.7,
            "reg_alpha": 1.0,
            "reg_lambda": 5.0,
            "is_unbalance": True,
            "verbosity": -1,
            "n_jobs": -1,
            "random_state": 42,
        }
    # regression
    if model_type == "xgboost":
        return {
            "n_estimators": 300,
            "max_depth": 3,
            "learning_rate": 0.05,
            "min_child_weight": 10,
            "subsample": 0.8,
            "colsample_bytree": 0.7,
            "reg_alpha": 1.0,
            "reg_lambda": 5.0,
            "early_stopping_rounds": 30,
            "objective": "reg:squarederror",
            "verbosity": 0,
            "n_jobs": -1,
            "random_state": 42,
        }
    return {
        "n_estimators": 300,
        "max_depth": 3,
        "num_leaves": 15,
        "learning_rate": 0.05,
        "min_child_samples": 15,
        "subsample": 0.8,
        "colsample_bytree": 0.7,
        "reg_alpha": 1.0,
        "reg_lambda": 5.0,
        "objective": "regression",
        "verbosity": -1,
        "n_jobs": -1,
        "random_state": 42,
    }


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    df_source: pd.DataFrame | None = None,
    task: str = "classification",
    test_size: float = 0.2,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """分层划分训练/测试集。优先按 DSGN_CYCLE 分层。"""
    stratify = None
    if df_source is not None and "DSGN_CYCLE" in df_source.columns:
        # 按 DSGN_CYCLE × 目标分箱 联合分层
        cycle = df_source.loc[y.index, "DSGN_CYCLE"]
        if task == "classification":
            stratify = (cycle.astype(str) + "_" + y.astype(str))
        else:
            bins = pd.qcut(y, q=4, labels=False, duplicates="drop")
            stratify = (cycle.astype(str) + "_" + bins.astype(str))
    elif task == "classification":
        stratify = y

    return train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=stratify,
    )


def train_single_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    task: str,
    model_type: str,
    params: dict | None = None,
) -> tuple:
    """训练单个模型，返回 (model, val_predictions)。"""
    if params is None:
        params = get_default_params(task, model_type)

    model = _create_model(task, model_type, params)
    log_info(f"训练 {model_type} {task} 模型...")

    if model_type == "xgboost":
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
    else:
        callbacks = [lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)]
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=callbacks,
        )

    # 验证集预测
    if task == "classification":
        val_pred = model.predict_proba(X_val)[:, 1]
    else:
        val_pred = model.predict(X_val)

    best_iter = getattr(model, "best_iteration", getattr(model, "best_iteration_", "N/A"))
    log_success(f"{model_type} {task} 训练完成 (best_iteration={best_iter})")
    return model, val_pred


def train_ensemble(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    task: str,
    small: bool = False,
) -> tuple[list, np.ndarray]:
    """训练 XGBoost + LightGBM 集成，返回 (models, ensemble_predictions)。"""
    models = []
    val_preds = []

    for model_type in ["xgboost", "lightgbm"]:
        params = get_default_params(task, model_type, small=small)
        model, val_pred = train_single_model(
            X_train, y_train, X_val, y_val, task, model_type, params=params,
        )
        models.append(model)
        val_preds.append(val_pred)

    # 简单平均集成
    ensemble_pred = np.mean(val_preds, axis=0)
    log_success(f"集成模型 ({task}): {len(models)} 个基学习器")
    return models, ensemble_pred


def cross_validate(
    X: pd.DataFrame,
    y: pd.Series,
    task: str,
    n_splits: int = 5,
    seed: int = 42,
) -> list[dict]:
    """5-fold 交叉验证，返回每折指标。"""
    log_info(f"开始 {n_splits}-fold 交叉验证 ({task})")
    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed) if task == "classification" else StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    # 对回归任务按分箱分层
    stratify = y if task == "classification" else pd.qcut(y, q=4, labels=False, duplicates="drop")

    fold_results = []
    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X, stratify)):
        X_tr, X_va = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_va = y.iloc[train_idx], y.iloc[val_idx]

        _, val_pred = train_ensemble(X_tr, y_tr, X_va, y_va, task)

        from src.evaluate import compute_classification_metrics, compute_regression_metrics
        if task == "classification":
            metrics = compute_classification_metrics(y_va, val_pred)
        else:
            metrics = compute_regression_metrics(y_va, val_pred)
        metrics["fold"] = fold_idx
        fold_results.append(metrics)
        log_info(f"  Fold {fold_idx + 1}/{n_splits}: " + "  ".join(f"{k}={v:.4f}" for k, v in metrics.items() if k != "fold"))

    # 汇总
    log_success(f"交叉验证完成 ({n_splits} folds)")
    return fold_results


def save_models(
    models: list, task: str, feature_names: list[str], dataset: str = "habs_training",
) -> Path:
    """保存训练好的模型。"""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    prefix = "" if dataset == "habs_training" else f"{dataset}_"
    path = MODEL_DIR / f"{prefix}{task}_ensemble.joblib"
    joblib.dump({"models": models, "feature_names": feature_names, "task": task, "dataset": dataset}, path)
    log_success(f"模型已保存: {path}")
    return path


def load_models(task: str, dataset: str = "habs_training") -> dict:
    """加载保存的模型。"""
    prefix = "" if dataset == "habs_training" else f"{dataset}_"
    path = MODEL_DIR / f"{prefix}{task}_ensemble.joblib"
    return joblib.load(path)
