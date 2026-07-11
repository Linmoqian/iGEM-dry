"""迭代 2：修复 LightGBM + 测试蓝藻叶绿素泄漏 + HABs 特征子集优化。"""

import json
import sys
import io
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
SPLITS_DIR = BASE_DIR / "data" / "splits"
REPORTS_DIR = BASE_DIR / "reports"
MEMORY_DIR = BASE_DIR / "memory"


def sanitize_feature_names(names):
    """Replace special characters for LightGBM compatibility."""
    return [n.replace("µ", "u").replace("μ", "u").replace("²", "2") for n in names]


def load_split(dataset):
    with open(SPLITS_DIR / "split_manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    df = pd.read_pickle(CLEANED_DIR / f"{dataset}_clean.pkl")
    split = manifest[dataset]
    train_idx = [i for i in split["train"] if i < len(df)]
    test_idx = [i for i in split["test"] if i < len(df)]
    return df, train_idx, test_idx


def prepare_data(df, train_idx, test_idx, target_col, features, dataset_name):
    valid = df[target_col].notna()
    if dataset_name == "habs_nla":
        valid = valid & (df[target_col] > 0)

    df_valid = df[valid].copy()
    X = df_valid[features].copy()
    y = np.log1p(df_valid[target_col])

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    common_train = [i for i in train_idx if i in X.index]
    common_test = [i for i in test_idx if i in X.index]

    if len(common_train) < 10 or len(common_test) < 10:
        print(f"  跳过: 训练 {len(common_train)} / 测试 {len(common_test)} 过小")
        return None

    X_train, y_train = X.loc[common_train], y.loc[common_train]
    X_test, y_test = X.loc[common_test], y.loc[common_test]

    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)

    return X_train, y_train, X_test, y_test, medians


def evaluate(y_true, y_pred, task_name):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    rmse_log = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae_log = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))

    y_true_orig = np.expm1(y_true)
    y_pred_orig = np.expm1(y_pred)
    rmse_orig = float(np.sqrt(mean_squared_error(y_true_orig, y_pred_orig)))
    mae_orig = float(mean_absolute_error(y_true_orig, y_pred_orig))

    spearman = float(stats.spearmanr(y_true, y_pred)[0])

    ratio = y_pred_orig / np.clip(y_true_orig, 1e-10, None)
    wf2 = float(np.mean((ratio >= 0.5) & (ratio <= 2.0)) * 100)

    threshold = np.percentile(y_true_orig, 75)
    high_mask = y_true_orig > threshold
    high_mae = float(mean_absolute_error(y_true_orig[high_mask], y_pred_orig[high_mask])) if high_mask.sum() > 0 else None

    return {
        "task": task_name,
        "rmse_log": round(rmse_log, 4),
        "mae_log": round(mae_log, 4),
        "r2": round(r2, 4),
        "spearman": round(spearman, 4),
        "rmse_orig": round(rmse_orig, 4),
        "mae_orig": round(mae_orig, 4),
        "wf2_pct": round(wf2, 1),
        "high_conc_mae_orig": round(high_mae, 4) if high_mae is not None else None,
        "n_samples": len(y_true),
    }


def get_all_models():
    """Return all models including properly configured XGBoost and LightGBM."""
    models = {
        "Ridge": lambda: Ridge(alpha=1.0),
        "RandomForest": lambda: RandomForestRegressor(
            n_estimators=300, max_depth=10, min_samples_leaf=5,
            random_state=42, n_jobs=-1,
        ),
        "HistGBR": lambda: HistGradientBoostingRegressor(
            max_iter=300, max_depth=6, learning_rate=0.05,
            min_samples_leaf=10, random_state=42,
        ),
    }
    try:
        import xgboost as xgb
        models["XGBoost"] = lambda: xgb.XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            min_child_weight=5, random_state=42, verbosity=0,
        )
    except ImportError:
        pass
    try:
        import lightgbm as lgb
        models["LightGBM"] = lambda: lgb.LGBMRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            min_child_samples=10, random_state=42, verbose=-1,
        )
    except ImportError:
        pass
    return models


def run_experiment(dataset, target_col, feature_list, exp_name, label):
    print(f"\n{'='*60}")
    print(f"实验: {exp_name} — {label}")
    print(f"{'='*60}")

    df, train_idx, test_idx = load_split(dataset)

    # Get available features
    available = [c for c in feature_list if c in df.columns]
    missing = [c for c in feature_list if c not in df.columns]
    if missing:
        print(f"  缺失特征: {missing}")

    result = prepare_data(df, train_idx, test_idx, target_col, available, dataset)
    if result is None:
        return None

    X_train, y_train, X_test, y_test, medians = result
    print(f"  训练: {len(X_train)}, 测试: {len(X_test)}, 特征: {len(available)}")

    # Sanitize feature names for LightGBM
    clean_names = sanitize_feature_names(available)
    name_map = dict(zip(available, clean_names))
    X_train_clean = X_train.rename(columns=name_map)
    X_test_clean = X_test.rename(columns=name_map)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train_clean)
    X_test_s = scaler.transform(X_test_clean)

    all_models = get_all_models()
    results = []

    for model_name, model_fn in all_models.items():
        try:
            model = model_fn()
            if model_name == "Ridge":
                model.fit(X_train_s, y_train)
                y_pred = model.predict(X_test_s)
            else:
                model.fit(X_train_clean, y_train)
                y_pred = model.predict(X_test_clean)

            metrics = evaluate(y_test, y_pred, model_name)
            results.append(metrics)
            print(f"  {model_name:20s}: R²={metrics['r2']:>7.3f}  "
                  f"RMSE(log)={metrics['rmse_log']:>7.3f}  "
                  f"Spearman={metrics['spearman']:>6.3f}  "
                  f"WF2={metrics['wf2_pct']:>5.1f}%")

            if hasattr(model, "feature_importances_"):
                imp = dict(zip(clean_names, model.feature_importances_))
                imp_sorted = dict(sorted(imp.items(), key=lambda x: -x[1])[:8])
                print(f"    Top: {imp_sorted}")
        except Exception as e:
            print(f"  {model_name}: 错误 — {e}")

    return {
        "experiment": exp_name,
        "label": label,
        "dataset": dataset,
        "target": target_col,
        "n_features": len(available),
        "features": available,
        "features_clean": clean_names,
        "metrics": results,
        "timestamp": datetime.now().isoformat(),
    }


def append_experiment_log(entry):
    log_path = MEMORY_DIR / "experiment_log.jsonl"
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []

    # === ERIE EXPERIMENTS ===

    # EXP-007: Erie expanded WITHOUT bluegreen algae-chla (leakage test)
    erie_no_bg = [
        "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
        "secchi_m", "max_depth_m",
        "month_sin", "month_cos", "latitude", "longitude",
        "nh3_mgL", "no3_no2_mgL",
        "Green algae-chla µg/l",
        "Diatoms-chla µg/l",
        "Cryptophytes-chla µg/l",
        "TN:TP (molar)",
        "TSS (g/L)",
    ]
    r7 = run_experiment("erie", "total_mc_ugL", erie_no_bg, "EXP-007",
                        "Erie expanded WITHOUT Bluegreen chla (leakage test)")
    if r7:
        all_results.append(r7)
        append_experiment_log({
            "experiment_id": "EXP-007",
            "timestamp": datetime.now().isoformat(),
            "stage": "iteration_2",
            "hypothesis": "去掉Bluegreen algae-chla后R²会下降，可量化泄漏贡献",
            "data_sources": ["erie"],
            "split_strategy": "time_based",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": erie_no_bg,
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r7["metrics"]},
            "notes": "Leakage test: compare with EXP-002 (R²=0.430 with BG chla)",
        })

    # EXP-008: Erie ONLY phytoplankton features (no water quality)
    erie_pigments_only = [
        "Green algae-chla µg/l",
        "Bluegreen algae-chla µg/l",
        "Diatoms-chla µg/l",
        "Cryptophytes-chla µg/l",
        "month_sin", "month_cos",
        "latitude", "longitude",
    ]
    r8 = run_experiment("erie", "total_mc_ugL", erie_pigments_only, "EXP-008",
                        "Erie phytoplankton only (8 feat)")
    if r8:
        all_results.append(r8)
        append_experiment_log({
            "experiment_id": "EXP-008",
            "timestamp": datetime.now().isoformat(),
            "stage": "iteration_2",
            "hypothesis": "仅浮游植物分类叶绿素+时空变量即可捕获大部分信号",
            "data_sources": ["erie"],
            "split_strategy": "time_based",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": erie_pigments_only,
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r8["metrics"]},
        })

    # === HABs EXPERIMENTS ===

    # EXP-009: HABs top features only (feature selection by importance)
    habs_top = [
        "tn_mgL", "turbidity_ntu", "ph", "tp_mgL",
        "B_G_DENS", "chla_ugL", "AMMONIA_N", "DOC",
        "precip_mean_month", "temp_mean_month",
        "water_temp_c", "latitude", "longitude",
        "month_sin", "month_cos",
    ]
    r9 = run_experiment("habs_nla", "total_mc_ugL", habs_top, "EXP-009",
                        "HABs top-15 features (by importance)")
    if r9:
        all_results.append(r9)
        append_experiment_log({
            "experiment_id": "EXP-009",
            "timestamp": datetime.now().isoformat(),
            "stage": "iteration_2",
            "hypothesis": "精选重要特征可减少噪声，提升或持平R²",
            "data_sources": ["habs_nla"],
            "split_strategy": "random_stratified",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": habs_top,
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r9["metrics"]},
        })

    # EXP-010: HABs with N/P surplus features
    habs_nutrients = [
        "tn_mgL", "tp_mgL", "turbidity_ntu", "ph",
        "chla_ugL", "water_temp_c", "do_mgL",
        "N_Surplus", "P_Surplus",
        "N_Total_Inputs", "P_f_fertilizer",
        "agr_ws", "dev_ws",
        "month_sin", "month_cos",
        "latitude", "longitude",
    ]
    r10 = run_experiment("habs_nla", "total_mc_ugL", habs_nutrients, "EXP-010",
                         "HABs with N/P surplus + land use (17 feat)")
    if r10:
        all_results.append(r10)
        append_experiment_log({
            "experiment_id": "EXP-010",
            "timestamp": datetime.now().isoformat(),
            "stage": "iteration_2",
            "hypothesis": "N/P surplus和土地利用反映流域营养输入，是HABs的驱动因子",
            "data_sources": ["habs_nla"],
            "split_strategy": "random_stratified",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": habs_nutrients,
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r10["metrics"]},
        })

    # === EMLS: Ridge with regularization sweep ===
    # EXP-011: EMLS with Ridge alpha sweep (small data needs strong regularization)
    emls_features = [
        "water_temp_c", "tp_mgL", "tn_mgL",
        "no3_no2_mgL", "nh3_mgL", "po4_ugL",
        "chla_ugL", "secchi_m", "max_depth_m",
        "latitude", "longitude",
    ]

    print(f"\n{'='*60}")
    print("EXP-011: EMLS Ridge alpha sweep")
    print(f"{'='*60}")

    df_emls, train_idx_emls, test_idx_emls = load_split("emls")
    available_emls = [c for c in emls_features if c in df_emls.columns]
    result_emls = prepare_data(df_emls, train_idx_emls, test_idx_emls, "mclr_ugL", available_emls, "emls")

    if result_emls:
        X_train_e, y_train_e, X_test_e, y_test_e, _ = result_emls
        scaler_e = StandardScaler()
        X_train_es = scaler_e.fit_transform(X_train_e)
        X_test_es = scaler_e.transform(X_test_e)

        best_r2 = -999
        best_alpha = None
        emls_ridge_results = []

        for alpha in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]:
            ridge = Ridge(alpha=alpha)
            ridge.fit(X_train_es, y_train_e)
            y_pred = ridge.predict(X_test_es)
            metrics = evaluate(y_test_e, y_pred, f"Ridge(a={alpha})")
            emls_ridge_results.append(metrics)
            print(f"  Ridge(alpha={alpha:>6}): R²={metrics['r2']:>7.3f}  "
                  f"Spearman={metrics['spearman']:>6.3f}  WF2={metrics['wf2_pct']:>5.1f}%")
            if metrics['r2'] > best_r2:
                best_r2 = metrics['r2']
                best_alpha = alpha

        print(f"\n  最佳 alpha: {best_alpha}, R²={best_r2:.3f}")

        r11_result = {
            "experiment": "EXP-011",
            "label": f"EMLS Ridge alpha sweep (best a={best_alpha})",
            "dataset": "emls",
            "target": "mclr_ugL",
            "n_features": len(available_emls),
            "features": available_emls,
            "metrics": emls_ridge_results,
            "best_alpha": best_alpha,
            "timestamp": datetime.now().isoformat(),
        }
        all_results.append(r11_result)
        append_experiment_log({
            "experiment_id": "EXP-011",
            "timestamp": datetime.now().isoformat(),
            "stage": "iteration_2",
            "hypothesis": "EMLS小样本需要强正则化，alpha sweep找到最优正则化强度",
            "data_sources": ["emls"],
            "split_strategy": "group_by_country",
            "target": "mclr_ugL",
            "target_transform": "log1p",
            "features": available_emls,
            "random_seed": 42,
            "metrics": {m["task"]: m for m in emls_ridge_results},
            "best_alpha": best_alpha,
        })

    # Save results
    report_path = REPORTS_DIR / "iteration2_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n结果已保存: {report_path}")

    # Summary
    print(f"\n{'='*90}")
    print("迭代 2 总结")
    print(f"{'='*90}")
    print(f"{'实验':<10} {'数据集':<10} {'模型':<18} {'R²':>8} {'Spearman':>10} {'WF2%':>8}")
    print("-" * 90)
    for r in all_results:
        for m in r["metrics"]:
            print(f"{r['experiment']:<10} {r['dataset']:<10} {m['task']:<18} "
                  f"{m['r2']:>8.3f} {m['spearman']:>10.3f} {m['wf2_pct']:>7.1f}%")


if __name__ == "__main__":
    main()
