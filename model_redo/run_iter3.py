"""迭代 3：跨数据集训练 + 合并数据集 + 时间稳定性分析。"""

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


def sanitize(names):
    return [n.replace("µ", "u").replace("μ", "u") for n in names]


def load_data(dataset):
    with open(SPLITS_DIR / "split_manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    df = pd.read_pickle(CLEANED_DIR / f"{dataset}_clean.pkl")
    split = manifest[dataset]
    train_idx = [i for i in split["train"] if i < len(df)]
    test_idx = [i for i in split["test"] if i < len(df)]
    return df, train_idx, test_idx


def evaluate(y_true, y_pred, task_name):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    rmse_log = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae_log = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    yo, yp = np.expm1(y_true), np.expm1(y_pred)
    spearman = float(stats.spearmanr(y_true, y_pred)[0])
    ratio = yp / np.clip(yo, 1e-10, None)
    wf2 = float(np.mean((ratio >= 0.5) & (ratio <= 2.0)) * 100)
    return {"task": task_name, "rmse_log": round(rmse_log, 4), "mae_log": round(mae_log, 4),
            "r2": round(r2, 4), "spearman": round(spearman, 4),
            "wf2_pct": round(wf2, 1), "n_samples": len(y_true)}


def get_models():
    models = {
        "Ridge": lambda: Ridge(alpha=1.0),
        "RF": lambda: RandomForestRegressor(n_estimators=300, max_depth=10, min_samples_leaf=5, random_state=42, n_jobs=-1),
    }
    try:
        import xgboost as xgb
        models["XGB"] = lambda: xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, min_child_weight=5, random_state=42, verbosity=0)
    except ImportError:
        pass
    try:
        import lightgbm as lgb
        models["LGBM"] = lambda: lgb.LGBMRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, min_child_samples=10, random_state=42, verbose=-1)
    except ImportError:
        pass
    return models


def run_eval(X_train, y_train, X_test, y_test, features_clean, label):
    """Run all models and return results."""
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_train)
    X_te_s = scaler.transform(X_test)

    results = []
    for name, fn in get_models().items():
        try:
            m = fn()
            if name == "Ridge":
                m.fit(X_tr_s, y_train)
                yp = m.predict(X_te_s)
            else:
                m.fit(X_train, y_train)
                yp = m.predict(X_test)
            met = evaluate(y_test, yp, name)
            results.append(met)
            print(f"    {name:8s}: R²={met['r2']:>7.3f}  Spearman={met['spearman']:>6.3f}  WF2={met['wf2_pct']:>5.1f}%")
            if hasattr(m, "feature_importances_"):
                imp = dict(zip(features_clean, m.feature_importances_))
                top = dict(sorted(imp.items(), key=lambda x: -x[1])[:5])
                print(f"      Top: {top}")
        except Exception as e:
            print(f"    {name}: 错误 — {e}")
    return results


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []

    # Common features between Erie and HABs
    COMMON_FEATURES = [
        "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
        "month_sin", "month_cos", "latitude", "longitude",
    ]

    # === EXP-012: Cross-dataset — Train HABs, Test Erie ===
    print(f"\n{'='*60}")
    print("EXP-012: Train HABs → Test Erie (cross-dataset)")
    print(f"{'='*60}")

    df_erie, _, test_erie = load_data("erie")
    df_habs, train_habs, _ = load_data("habs_nla")

    features_avail = [c for c in COMMON_FEATURES if c in df_erie.columns and c in df_habs.columns]
    features_clean = sanitize(features_avail)

    # Prepare HABs training data
    habs_valid = df_habs["total_mc_ugL"].notna() & (df_habs["total_mc_ugL"] > 0)
    df_hv = df_habs[habs_valid].copy()
    X_h = df_hv[features_avail].copy()
    for c in X_h.columns:
        X_h[c] = pd.to_numeric(X_h[c], errors="coerce")
    y_h = np.log1p(df_hv["total_mc_ugL"])

    common_h_train = [i for i in train_habs if i in X_h.index]
    X_h_train = X_h.loc[common_h_train].rename(columns=dict(zip(features_avail, features_clean)))
    y_h_train = y_h.loc[common_h_train]

    # Prepare Erie test data
    erie_valid = df_erie["total_mc_ugL"].notna()
    df_ev = df_erie[erie_valid].copy()
    X_e = df_ev[features_avail].copy()
    for c in X_e.columns:
        X_e[c] = pd.to_numeric(X_e[c], errors="coerce")
    y_e = np.log1p(df_ev["total_mc_ugL"])

    common_e_test = [i for i in test_erie if i in X_e.index]
    X_e_test = X_e.loc[common_e_test].rename(columns=dict(zip(features_avail, features_clean)))
    y_e_test = y_e.loc[common_e_test]

    # Impute
    med = X_h_train.median()
    X_h_train = X_h_train.fillna(med)
    X_e_test = X_e_test.fillna(med)

    print(f"  HABs 训练: {len(X_h_train)}, Erie 测试: {len(X_e_test)}, 特征: {len(features_clean)}")
    r12 = run_eval(X_h_train, y_h_train, X_e_test, y_e_test, features_clean, "HABs→Erie")
    all_results.append({"experiment": "EXP-012", "label": "Train HABs → Test Erie", "metrics": r12})

    # === EXP-013: Cross-dataset — Train Erie, Test HABs ===
    print(f"\n{'='*60}")
    print("EXP-013: Train Erie → Test HABs (cross-dataset)")
    print(f"{'='*60}")

    erie_train_valid = df_erie["total_mc_ugL"].notna()
    df_etv = df_erie[erie_train_valid].copy()
    X_et = df_etv[features_avail].copy()
    for c in X_et.columns:
        X_et[c] = pd.to_numeric(X_et[c], errors="coerce")
    y_et = np.log1p(df_etv["total_mc_ugL"])

    _, train_erie, _ = load_data("erie")
    common_e_train = [i for i in train_erie if i in X_et.index]
    X_e_train = X_et.loc[common_e_train].rename(columns=dict(zip(features_avail, features_clean)))
    y_e_train = y_et.loc[common_e_train]

    habs_test_valid = df_habs["total_mc_ugL"].notna() & (df_habs["total_mc_ugL"] > 0)
    df_htv = df_habs[habs_test_valid].copy()
    X_ht = df_htv[features_avail].copy()
    for c in X_ht.columns:
        X_ht[c] = pd.to_numeric(X_ht[c], errors="coerce")
    y_ht = np.log1p(df_htv["total_mc_ugL"])

    _, _, test_habs = load_data("habs_nla")
    common_h_test = [i for i in test_habs if i in X_ht.index]
    X_h_test = X_ht.loc[common_h_test].rename(columns=dict(zip(features_avail, features_clean)))
    y_h_test = y_ht.loc[common_h_test]

    med2 = X_e_train.median()
    X_e_train = X_e_train.fillna(med2)
    X_h_test = X_h_test.fillna(med2)

    print(f"  Erie 训练: {len(X_e_train)}, HABs 测试: {len(X_h_test)}, 特征: {len(features_clean)}")
    r13 = run_eval(X_e_train, y_e_train, X_h_test, y_h_test, features_clean, "Erie→HABs")
    all_results.append({"experiment": "EXP-013", "label": "Train Erie → Test HABs", "metrics": r13})

    # === EXP-014: Combined Erie + HABs with data_source indicator ===
    print(f"\n{'='*60}")
    print("EXP-014: Combined Erie+HABs (with is_erie feature)")
    print(f"{'='*60}")

    COMBINED_FEATURES = COMMON_FEATURES + ["is_erie"]

    # Build combined dataset
    df_e2 = df_erie[erie_valid].copy()
    df_e2["is_erie"] = 1
    df_h2 = df_habs[habs_valid].copy()
    df_h2["is_erie"] = 0

    # Use only common features + is_erie
    avail_comb = [c for c in COMBINED_FEATURES if c in df_e2.columns and c in df_h2.columns]
    clean_comb = sanitize(avail_comb)

    X_e2 = df_e2[avail_comb + ["total_mc_ugL"]].copy()
    X_h2 = df_h2[avail_comb + ["total_mc_ugL"]].copy()

    for c in avail_comb:
        X_e2[c] = pd.to_numeric(X_e2[c], errors="coerce")
        X_h2[c] = pd.to_numeric(X_h2[c], errors="coerce")

    # Add year for time-based split
    X_e2["year"] = df_erie.loc[X_e2.index, "year"] if "year" in df_erie.columns else 0
    X_h2["year"] = df_habs.loc[X_h2.index, "year"] if "year" in df_habs.columns else 0
    X_e2["data_source"] = "erie"
    X_h2["data_source"] = "habs_nla"

    combined = pd.concat([X_e2, X_h2], ignore_index=False)
    combined = combined.sort_index()

    # Time-based split for Erie, random for HABs, combined
    erie_train_mask = combined.index.isin(train_erie) & (combined["data_source"] == "erie")
    erie_test_mask = combined.index.isin(test_erie) & (combined["data_source"] == "erie")
    habs_train_mask = combined.index.isin(train_habs) & (combined["data_source"] == "habs_nla")
    habs_test_mask = combined.index.isin(test_habs) & (combined["data_source"] == "habs_nla")

    train_mask = erie_train_mask | habs_train_mask
    test_mask = erie_test_mask | habs_test_mask

    X_c_train = combined.loc[train_mask, avail_comb].rename(columns=dict(zip(avail_comb, clean_comb)))
    y_c_train = np.log1p(combined.loc[train_mask, "total_mc_ugL"])
    X_c_test = combined.loc[test_mask, avail_comb].rename(columns=dict(zip(avail_comb, clean_comb)))
    y_c_test = np.log1p(combined.loc[test_mask, "total_mc_ugL"])

    med3 = X_c_train.median()
    X_c_train = X_c_train.fillna(med3)
    X_c_test = X_c_test.fillna(med3)

    print(f"  训练: {len(X_c_train)}, 测试: {len(X_c_test)}, 特征: {len(clean_comb)}")
    r14_all = run_eval(X_c_train, y_c_train, X_c_test, y_c_test, clean_comb, "Combined all")
    all_results.append({"experiment": "EXP-014", "label": "Combined Erie+HABs (all test)", "metrics": r14_all})

    # Test on Erie only
    erie_test_data = combined.loc[erie_test_mask]
    X_ce_test = erie_test_data[avail_comb].rename(columns=dict(zip(avail_comb, clean_comb))).fillna(med3)
    y_ce_test = np.log1p(erie_test_data["total_mc_ugL"])
    print(f"\n  仅 Erie 测试: {len(X_ce_test)}")
    r14_erie = run_eval(X_c_train, y_c_train, X_ce_test, y_ce_test, clean_comb, "Combined→Erie test")
    all_results.append({"experiment": "EXP-014b", "label": "Combined train → Erie test", "metrics": r14_erie})

    # Test on HABs only
    habs_test_data = combined.loc[habs_test_mask]
    X_ch_test = habs_test_data[avail_comb].rename(columns=dict(zip(avail_comb, clean_comb))).fillna(med3)
    y_ch_test = np.log1p(habs_test_data["total_mc_ugL"])
    print(f"  仅 HABs 测试: {len(X_ch_test)}")
    r14_habs = run_eval(X_c_train, y_c_train, X_ch_test, y_ch_test, clean_comb, "Combined→HABs test")
    all_results.append({"experiment": "EXP-014c", "label": "Combined train → HABs test", "metrics": r14_habs})

    # === EXP-015: Erie time stability — train on early years, test on late years ===
    print(f"\n{'='*60}")
    print("EXP-015: Erie time stability (train 2013-2019, test 2020-2024)")
    print(f"{'='*60}")

    erie_expanded = [
        "water_temp_c", "chla_ugL", "tn_mgL", "tp_mgL",
        "secchi_m", "max_depth_m",
        "month_sin", "month_cos", "latitude", "longitude",
        "nh3_mgL", "no3_no2_mgL",
        "Green algae-chla µg/l",
        "Bluegreen algae-chla µg/l",
        "Diatoms-chla µg/l",
        "Cryptophytes-chla µg/l",
        "TN:TP (molar)",
    ]
    avail_e15 = [c for c in erie_expanded if c in df_erie.columns]
    clean_e15 = sanitize(avail_e15)

    df_e15 = df_erie[erie_valid].copy()
    X_e15 = df_e15[avail_e15].copy()
    for c in X_e15.columns:
        X_e15[c] = pd.to_numeric(X_e15[c], errors="coerce")
    y_e15 = np.log1p(df_e15["total_mc_ugL"])
    X_e15["year"] = df_e15["year"]

    # Split by year
    early_mask = X_e15["year"] <= 2019
    late_mask = X_e15["year"] > 2019

    X_early = X_e15.loc[early_mask, avail_e15].rename(columns=dict(zip(avail_e15, clean_e15)))
    y_early = y_e15.loc[early_mask]
    X_late = X_e15.loc[late_mask, avail_e15].rename(columns=dict(zip(avail_e15, clean_e15)))
    y_late = y_e15.loc[late_mask]

    med_e15 = X_early.median()
    X_early = X_early.fillna(med_e15)
    X_late = X_late.fillna(med_e15)

    print(f"  训练 (≤2019): {len(X_early)}, 测试 (>2019): {len(X_late)}")
    r15 = run_eval(X_early, y_early, X_late, y_late, clean_e15, "Erie early→late")
    all_results.append({"experiment": "EXP-015", "label": "Erie 2013-2019 → 2020-2024", "metrics": r15})

    # Also reverse: train late, test early
    print(f"\n  反向: 训练 (>2019): {len(X_late)}, 测试 (≤2019): {len(X_early)}")
    r15b = run_eval(X_late, y_late, X_early, y_early, clean_e15, "Erie late→early")
    all_results.append({"experiment": "EXP-015b", "label": "Erie 2020-2024 → 2013-2019", "metrics": r15b})

    # Save
    report_path = REPORTS_DIR / "iteration3_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n结果已保存: {report_path}")

    # Summary
    print(f"\n{'='*90}")
    print("迭代 3 总结")
    print(f"{'='*90}")
    for r in all_results:
        print(f"\n{r['experiment']}: {r['label']}")
        for m in r["metrics"]:
            print(f"  {m['task']:8s}: R²={m['r2']:>7.3f}  Spearman={m['spearman']:>6.3f}  WF2={m['wf2_pct']:>5.1f}%")


if __name__ == "__main__":
    main()
