"""Baseline 模型训练 — DummyRegressor / Ridge / RandomForest。"""

import json
import sys
import io
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
SPLITS_DIR = BASE_DIR / "data" / "splits"
REPORTS_DIR = BASE_DIR / "reports"


def load_split(dataset: str) -> tuple:
    """加载数据和划分。"""
    with open(SPLITS_DIR / "split_manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)

    df = pd.read_pickle(CLEANED_DIR / f"{dataset}_clean.pkl")
    split = manifest[dataset]
    train_idx = [i for i in split["train"] if i < len(df)]
    test_idx = [i for i in split["test"] if i < len(df)]
    return df, train_idx, test_idx


def get_features_and_target(df: pd.DataFrame, dataset: str, target_col: str = "total_mc_ugL"):
    """提取特征和目标变量。"""
    # Common features across datasets
    feature_candidates = [
        "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
        "ph", "do_mgL", "turbidity_ntu", "secchi_m", "max_depth_m",
        "month_sin", "month_cos", "latitude", "longitude",
    ]
    features = [c for c in feature_candidates if c in df.columns]
    valid = df[target_col].notna()
    if dataset == "habs_nla":
        valid = valid & (df[target_col] > 0)

    df_valid = df[valid].copy()
    X = df_valid[features].copy()
    y = np.log1p(df_valid[target_col])  # log1p transform
    return X, y, features


def evaluate(y_true, y_pred, task_name: str) -> dict:
    """计算评估指标。"""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))

    # Back-transform to original scale
    y_true_orig = np.expm1(y_true)
    y_pred_orig = np.expm1(y_pred)
    rmse_orig = float(np.sqrt(mean_squared_error(y_true_orig, y_pred_orig)))
    mae_orig = float(mean_absolute_error(y_true_orig, y_pred_orig))

    # Spearman
    spearman = float(stats.spearmanr(y_true, y_pred)[0])

    # Within factor of 2
    ratio = y_pred_orig / np.clip(y_true_orig, 1e-10, None)
    wf2 = float(np.mean((ratio >= 0.5) & (ratio <= 2.0)) * 100)

    return {
        "task": task_name,
        "rmse_log": rmse,
        "mae_log": mae,
        "r2": r2,
        "spearman": spearman,
        "rmse_orig": rmse_orig,
        "mae_orig": mae_orig,
        "wf2_pct": wf2,
        "n_samples": len(y_true),
    }


def run_baseline(dataset: str, target_col: str = "total_mc_ugL"):
    """运行单个数据集的 baseline。"""
    print(f"\n{'='*50}")
    print(f"Baseline: {dataset}")
    print(f"{'='*50}")

    df, train_idx, test_idx = load_split(dataset)
    X, y, features = get_features_and_target(df, dataset, target_col)

    if len(X) == 0:
        print(f"  跳过: 无有效样本")
        return None

    # Split
    common_train = [i for i in train_idx if i in X.index]
    common_test = [i for i in test_idx if i in X.index]

    if len(common_train) < 10 or len(common_test) < 10:
        print(f"  跳过: 训练集 {len(common_train)} 或测试集 {len(common_test)} 过小")
        return None

    X_train, y_train = X.loc[common_train], y.loc[common_train]
    X_test, y_test = X.loc[common_test], y.loc[common_test]

    # Handle NaN for models that need it - force numeric first
    for col in X_train.columns:
        X_train[col] = pd.to_numeric(X_train[col], errors="coerce")
        X_test[col] = pd.to_numeric(X_test[col], errors="coerce")
    X_train = X_train.fillna(X_train.median())
    X_test = X_test.fillna(X_train.median())

    print(f"  训练: {len(X_train)} 行, 测试: {len(X_test)} 行")
    print(f"  特征: {features}")
    print(f"  目标: {target_col} (log1p)")

    results = []

    # 1. DummyRegressor (mean)
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(X_train, y_train)
    y_pred_dummy = dummy.predict(X_test)
    metrics_dummy = evaluate(y_test, y_pred_dummy, "DummyRegressor")
    results.append(metrics_dummy)
    print(f"  DummyRegressor: R²={metrics_dummy['r2']:.3f}, RMSE(log)={metrics_dummy['rmse_log']:.3f}, WF2={metrics_dummy['wf2_pct']:.1f}%")

    # 2. Ridge
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train_s, y_train)
    y_pred_ridge = ridge.predict(X_test_s)
    metrics_ridge = evaluate(y_test, y_pred_ridge, "Ridge")
    results.append(metrics_ridge)
    print(f"  Ridge: R²={metrics_ridge['r2']:.3f}, RMSE(log)={metrics_ridge['rmse_log']:.3f}, WF2={metrics_ridge['wf2_pct']:.1f}%")

    # 3. RandomForest
    rf = RandomForestRegressor(
        n_estimators=200, max_depth=8, min_samples_leaf=10,
        random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    metrics_rf = evaluate(y_test, y_pred_rf, "RandomForest")
    results.append(metrics_rf)
    print(f"  RandomForest: R²={metrics_rf['r2']:.3f}, RMSE(log)={metrics_rf['rmse_log']:.3f}, WF2={metrics_rf['wf2_pct']:.1f}%")

    # Feature importance
    importance = dict(zip(features, rf.feature_importances_))
    importance_sorted = dict(sorted(importance.items(), key=lambda x: -x[1]))
    print(f"  RF 特征重要性: {importance_sorted}")

    return {
        "dataset": dataset,
        "metrics": results,
        "feature_importance": importance_sorted,
        "n_features": len(features),
        "features": features,
    }


def main():
    all_results = []

    # Task A: Total MC
    for dataset, target in [("erie", "total_mc_ugL"), ("habs_nla", "total_mc_ugL")]:
        result = run_baseline(dataset, target)
        if result:
            all_results.append(result)

    # Task B: MC-LR
    for dataset, target in [("emls", "mclr_ugL")]:
        result = run_baseline(dataset, target)
        if result:
            all_results.append(result)

    # Save report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "baseline_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n结果已保存: {report_path}")

    # Print summary table
    print(f"\n{'='*70}")
    print("Baseline 总结")
    print(f"{'='*70}")
    print(f"{'数据集':<12} {'模型':<16} {'R²':>8} {'RMSE(log)':>10} {'MAE(log)':>10} {'Spearman':>10} {'WF2%':>8}")
    print("-" * 70)
    for r in all_results:
        for m in r["metrics"]:
            print(f"{r['dataset']:<12} {m['task']:<16} {m['r2']:>8.3f} {m['rmse_log']:>10.3f} {m['mae_log']:>10.3f} {m['spearman']:>10.3f} {m['wf2_pct']:>7.1f}%")


if __name__ == "__main__":
    main()
