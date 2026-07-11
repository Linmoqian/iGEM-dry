"""增强版 baseline 训练 — DummyRegressor / Ridge / RF / XGBoost / LightGBM + 扩展特征集。"""

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

# --- Feature definitions per dataset ---

# Features that could leak (MC-related, excluded from prediction features)
ERIE_LEAKAGE_COLS = {
    "Extracellular Microcystin (µg/L)",
    "total_mc_ugL",
}

# Lake Erie expanded features (safe for deployment)
ERIE_FEATURES_SAFE = [
    "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
    "secchi_m", "max_depth_m",
    "month_sin", "month_cos", "latitude", "longitude",
    "nh3_mgL", "no3_no2_mgL",
    # Phytoplankton group chlorophyll — measured via fluorescence probe
    # NOTE: Bluegreen algae-chla may have information leakage risk
    # (measured same event as MC). Including with flag.
    "Green algae-chla µg/l",
    "Bluegreen algae-chla µg/l",
    "Diatoms-chla µg/l",
    "Cryptophytes-chla µg/l",
    "TN:TP (molar)",
    "TSS (g/L)",
]

# HABs NLA expanded features
HABS_FEATURES_SAFE = [
    "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
    "ph", "do_mgL", "turbidity_ntu", "max_depth_m",
    "month_sin", "month_cos", "latitude", "longitude",
    "AMMONIA_N", "NITRATE_N", "DOC",
    "B_G_DENS",  # Blue-green density (phycocyanin fluorescence proxy)
    "precip_mean_month", "temp_mean_month",
    "agr_ws", "dev_ws", "fst_ws",
    "lakemorpho_fetch",
    "SlopeWs", "ElevWs",
    "N_Surplus", "P_Surplus",
]

# EMLS expanded features (MC variants excluded — leakage)
EMLS_FEATURES_SAFE = [
    "water_temp_c", "tp_mgL", "tn_mgL",
    "no3_no2_mgL", "nh3_mgL", "po4_ugL",
    "chla_ugL", "secchi_m", "max_depth_m",
    "month_sin", "month_cos", "latitude", "longitude",
    "Altitude_m", "MeanDepth_m", "ThermoclineDepth_m",
    # Phytoplankton pigments (NOT MC — these are taxonomic markers)
    "Zeaxanthin_ugL",      # Cyanobacteria marker
    "Fucoxanthin_ugL",     # Diatom marker
    "Alloxanthin_ugL",     # Cryptophyte marker
    "Echinenone_ugL",      # Cyanobacteria marker
    "Lutein_ugL",          # Chlorophyte marker
    "Chlorophyllb_ugL",    # Green algae marker
    "Chlorophyllc2_ugL",   # Chromophyte marker
    "Peridinin_ugL",       # Dinoflagellate marker
    "Diadinoxanthin_ugL",  # Photoprotective pigment
    "Diatoxanthin_ugL",    # Photoprotective pigment
    "Violaxanthin_ugL",    # Photoprotective pigment
]


def load_split(dataset: str) -> tuple:
    """加载数据和划分。"""
    with open(SPLITS_DIR / "split_manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)

    df = pd.read_pickle(CLEANED_DIR / f"{dataset}_clean.pkl")
    split = manifest[dataset]
    train_idx = [i for i in split["train"] if i < len(df)]
    test_idx = [i for i in split["test"] if i < len(df)]
    return df, train_idx, test_idx


def get_features(df, feature_list):
    """提取可用特征。"""
    available = [c for c in feature_list if c in df.columns]
    missing = [c for c in feature_list if c not in df.columns]
    if missing:
        print(f"  缺失特征（跳过）: {missing}")
    return available


def prepare_data(df, train_idx, test_idx, target_col, features, dataset_name):
    """准备训练和测试数据。"""
    valid = df[target_col].notna()
    # For HABs, only use detected samples for regression
    if dataset_name == "habs_nla":
        valid = valid & (df[target_col] > 0)

    df_valid = df[valid].copy()
    X = df_valid[features].copy()
    y = np.log1p(df_valid[target_col])

    # Force numeric
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    common_train = [i for i in train_idx if i in X.index]
    common_test = [i for i in test_idx if i in X.index]

    if len(common_train) < 10 or len(common_test) < 10:
        print(f"  跳过: 训练 {len(common_train)} / 测试 {len(common_test)} 过小")
        return None

    X_train, y_train = X.loc[common_train], y.loc[common_train]
    X_test, y_test = X.loc[common_test], y.loc[common_test]

    # Impute with training median
    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)

    return X_train, y_train, X_test, y_test, medians


def evaluate(y_true, y_pred, task_name):
    """计算评估指标。"""
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

    # High-concentration sample analysis (>75th percentile)
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


def get_models():
    """返回所有模型配置。"""
    return {
        "DummyRegressor": lambda: DummyRegressor(strategy="mean"),
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


def get_xgb_lgbm_models():
    """返回 XGBoost 和 LightGBM 模型（若可用）。"""
    models = {}
    try:
        import xgboost as xgb
        models["XGBoost"] = lambda: xgb.XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            min_child_weight=5, random_state=42,
            verbosity=0,
        )
    except ImportError:
        print("  [警告] XGBoost 不可用")
    try:
        import lightgbm as lgb
        models["LightGBM"] = lambda: lgb.LGBMRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            min_child_samples=10, random_state=42,
            verbose=-1,
        )
    except ImportError:
        print("  [警告] LightGBM 不可用")
    return models


def run_experiment(dataset, target_col, feature_list, exp_name, label):
    """运行单个数据集的全部模型。"""
    print(f"\n{'='*60}")
    print(f"实验: {exp_name} — {label}")
    print(f"数据集: {dataset}, 目标: {target_col}")
    print(f"{'='*60}")

    df, train_idx, test_idx = load_split(dataset)
    features = get_features(df, feature_list)
    result = prepare_data(df, train_idx, test_idx, target_col, features, dataset)

    if result is None:
        return None

    X_train, y_train, X_test, y_test, medians = result
    print(f"  训练: {len(X_train)}, 测试: {len(X_test)}, 特征: {len(features)}")

    # Scale for linear models
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    all_models = get_models()
    all_models.update(get_xgb_lgbm_models())

    results = []
    for model_name, model_fn in all_models.items():
        try:
            model = model_fn()
            if model_name in ("Ridge",):
                model.fit(X_train_s, y_train)
                y_pred = model.predict(X_test_s)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

            metrics = evaluate(y_test, y_pred, model_name)
            results.append(metrics)
            print(f"  {model_name:20s}: R²={metrics['r2']:>7.3f}  "
                  f"RMSE(log)={metrics['rmse_log']:>7.3f}  "
                  f"Spearman={metrics['spearman']:>6.3f}  "
                  f"WF2={metrics['wf2_pct']:>5.1f}%")

            # Feature importance for tree models
            if hasattr(model, "feature_importances_"):
                imp = dict(zip(features, model.feature_importances_))
                imp_sorted = dict(sorted(imp.items(), key=lambda x: -x[1])[:10])
                print(f"    Top features: {imp_sorted}")
        except Exception as e:
            print(f"  {model_name}: 错误 — {e}")

    return {
        "experiment": exp_name,
        "label": label,
        "dataset": dataset,
        "target": target_col,
        "n_features": len(features),
        "features": features,
        "metrics": results,
        "timestamp": datetime.now().isoformat(),
    }


def append_experiment_log(entry):
    """追加实验日志。"""
    log_path = MEMORY_DIR / "experiment_log.jsonl"
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []

    # --- Experiment 1: Lake Erie baseline (10 features, as before) ---
    erie_basic = [
        "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
        "secchi_m", "max_depth_m", "month_sin", "month_cos",
        "latitude", "longitude",
    ]
    r1 = run_experiment("erie", "total_mc_ugL", erie_basic, "EXP-001", "Lake Erie baseline (10 feat)")
    if r1:
        all_results.append(r1)
        append_experiment_log({
            "experiment_id": "EXP-001",
            "timestamp": datetime.now().isoformat(),
            "stage": "baseline_enhanced",
            "hypothesis": "复现原 baseline 作为对照",
            "data_sources": ["erie"],
            "data_version": "erie_clean.pkl",
            "split_strategy": "time_based",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": erie_basic,
            "model": "Dummy/Ridge/RF/HistGBR/XGB/LGBM",
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r1["metrics"]} if r1 else {},
            "notes": "10-feature baseline replication",
        })

    # --- Experiment 2: Lake Erie expanded features ---
    r2 = run_experiment("erie", "total_mc_ugL", ERIE_FEATURES_SAFE, "EXP-002",
                        "Lake Erie expanded (phytoplankton + nutrients)")
    if r2:
        all_results.append(r2)
        append_experiment_log({
            "experiment_id": "EXP-002",
            "timestamp": datetime.now().isoformat(),
            "stage": "baseline_enhanced",
            "hypothesis": "添加浮游植物分类叶绿素+营养盐细分+TN:TP+TSS可提升预测",
            "data_sources": ["erie"],
            "data_version": "erie_clean.pkl",
            "split_strategy": "time_based",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": ERIE_FEATURES_SAFE,
            "model": "Dummy/Ridge/RF/HistGBR/XGB/LGBM",
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r2["metrics"]} if r2 else {},
            "notes": "Bluegreen algae-chla included with leakage risk flag",
        })

    # --- Experiment 3: HABs NLA baseline (12 features, as before) ---
    habs_basic = [
        "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
        "ph", "do_mgL", "turbidity_ntu", "max_depth_m",
        "month_sin", "month_cos", "latitude", "longitude",
    ]
    r3 = run_experiment("habs_nla", "total_mc_ugL", habs_basic, "EXP-003",
                        "HABs NLA baseline (12 feat)")
    if r3:
        all_results.append(r3)
        append_experiment_log({
            "experiment_id": "EXP-003",
            "timestamp": datetime.now().isoformat(),
            "stage": "baseline_enhanced",
            "hypothesis": "复现原 baseline 作为对照",
            "data_sources": ["habs_nla"],
            "data_version": "habs_nla_clean.pkl",
            "split_strategy": "random_stratified",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": habs_basic,
            "model": "Dummy/Ridge/RF/HistGBR/XGB/LGBM",
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r3["metrics"]} if r3 else {},
        })

    # --- Experiment 4: HABs NLA expanded features ---
    r4 = run_experiment("habs_nla", "total_mc_ugL", HABS_FEATURES_SAFE, "EXP-004",
                        "HABs NLA expanded (land use + nutrients + climate)")
    if r4:
        all_results.append(r4)
        append_experiment_log({
            "experiment_id": "EXP-004",
            "timestamp": datetime.now().isoformat(),
            "stage": "baseline_enhanced",
            "hypothesis": "添加土地利用+气候+N/P预算特征可提升预测",
            "data_sources": ["habs_nla"],
            "data_version": "habs_nla_clean.pkl",
            "split_strategy": "random_stratified",
            "target": "total_mc_ugL",
            "target_transform": "log1p",
            "features": HABS_FEATURES_SAFE,
            "model": "Dummy/Ridge/RF/HistGBR/XGB/LGBM",
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r4["metrics"]} if r4 else {},
        })

    # --- Experiment 5: EMLS MC-LR baseline (10 features) ---
    emls_basic = [
        "water_temp_c", "tp_mgL", "tn_mgL",
        "chla_ugL", "secchi_m", "max_depth_m",
        "month_sin", "month_cos", "latitude", "longitude",
    ]
    r5 = run_experiment("emls", "mclr_ugL", emls_basic, "EXP-005",
                        "EMLS MC-LR baseline (10 feat)")
    if r5:
        all_results.append(r5)
        append_experiment_log({
            "experiment_id": "EXP-005",
            "timestamp": datetime.now().isoformat(),
            "stage": "baseline_enhanced",
            "hypothesis": "复现原 baseline 作为对照",
            "data_sources": ["emls"],
            "data_version": "emls_clean.pkl",
            "split_strategy": "group_by_country",
            "target": "mclr_ugL",
            "target_transform": "log1p",
            "features": emls_basic,
            "model": "Dummy/Ridge/RF/HistGBR/XGB/LGBM",
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r5["metrics"]} if r5 else {},
        })

    # --- Experiment 6: EMLS MC-LR expanded features ---
    r6 = run_experiment("emls", "mclr_ugL", EMLS_FEATURES_SAFE, "EXP-006",
                        "EMLS MC-LR expanded (pigments + lake morphology)")
    if r6:
        all_results.append(r6)
        append_experiment_log({
            "experiment_id": "EXP-006",
            "timestamp": datetime.now().isoformat(),
            "stage": "baseline_enhanced",
            "hypothesis": "添加浮游植物色素标记+湖泊形态可提升MC-LR预测",
            "data_sources": ["emls"],
            "data_version": "emls_clean.pkl",
            "split_strategy": "group_by_country",
            "target": "mclr_ugL",
            "target_transform": "log1p",
            "features": EMLS_FEATURES_SAFE,
            "model": "Dummy/Ridge/RF/HistGBR/XGB/LGBM",
            "random_seed": 42,
            "metrics": {m["task"]: m for m in r6["metrics"]} if r6 else {},
        })

    # Save results
    report_path = REPORTS_DIR / "enhanced_baseline_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n结果已保存: {report_path}")

    # Summary table
    print(f"\n{'='*90}")
    print("增强 Baseline 总结")
    print(f"{'='*90}")
    print(f"{'实验':<10} {'数据集':<10} {'模型':<18} {'R²':>8} {'RMSE(log)':>10} {'Spearman':>10} {'WF2%':>8}")
    print("-" * 90)
    for r in all_results:
        for m in r["metrics"]:
            print(f"{r['experiment']:<10} {r['dataset']:<10} {m['task']:<18} "
                  f"{m['r2']:>8.3f} {m['rmse_log']:>10.3f} "
                  f"{m['spearman']:>10.3f} {m['wf2_pct']:>7.1f}%")


if __name__ == "__main__":
    main()
