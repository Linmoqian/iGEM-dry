"""数据划分脚本 — 按时间/站点/数据源划分训练/验证/测试集。"""

import json
import sys
import io
from pathlib import Path

import pandas as pd
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
SPLITS_DIR = BASE_DIR / "data" / "splits"
SPLITS_DIR.mkdir(parents=True, exist_ok=True)


def split_lake_erie(df: pd.DataFrame, seed: int = 42) -> dict:
    """Lake Erie: 按年份划分 — 2013-2022 训练, 2023-2024 测试。"""
    df = df.copy()
    if "year" not in df.columns:
        df["year"] = pd.to_datetime(df["sample_date"], errors="coerce").dt.year

    # Time-based split
    train_mask = df["year"] <= 2022
    test_mask = df["year"] > 2022

    train_idx = df.index[train_mask].tolist()
    test_idx = df.index[test_mask].tolist()

    # If test set too small, use 80/20 random split with group by year
    if len(test_idx) < 50:
        print(f"  时间划分测试集过小 ({len(test_idx)}), 改用随机划分")
        np.random.seed(seed)
        years = df["year"].unique()
        np.random.shuffle(years)
        n_test_years = max(1, len(years) // 5)
        test_years = set(years[:n_test_years])
        train_mask = ~df["year"].isin(test_years)
        test_mask = df["year"].isin(test_years)
        train_idx = df.index[train_mask].tolist()
        test_idx = df.index[test_mask].tolist()

    return {
        "train": train_idx,
        "test": test_idx,
        "strategy": "time_based",
        "train_years": sorted(df.loc[train_idx, "year"].dropna().unique().tolist()),
        "test_years": sorted(df.loc[test_idx, "year"].dropna().unique().tolist()),
        "n_train": len(train_idx),
        "n_test": len(test_idx),
    }


def split_habs(df: pd.DataFrame, seed: int = 42) -> dict:
    """HABs Training: 按 DSGN_CYCLE 分层随机划分。"""
    df = df.copy()
    target = "total_mc_ugL"
    valid = df[target].notna() & (df[target] > 0)
    df_valid = df[valid].copy()

    # Random 80/20 split
    np.random.seed(seed)
    n = len(df_valid)
    indices = np.random.permutation(n)
    n_test = max(int(n * 0.2), 50)
    test_idx = df_valid.index[indices[:n_test]].tolist()
    train_idx = df_valid.index[indices[n_test:]].tolist()

    return {
        "train": train_idx,
        "test": test_idx,
        "strategy": "random_stratified",
        "n_train": len(train_idx),
        "n_test": len(test_idx),
        "note": "仅使用 MICX>0 样本",
    }


def split_emls(df: pd.DataFrame, seed: int = 42) -> dict:
    """EMLS Europe: 按国家 group split。"""
    df = df.copy()
    np.random.seed(seed)

    countries = df["country"].dropna().unique()
    np.random.shuffle(countries)
    n_test_countries = max(1, len(countries) // 5)
    test_countries = set(countries[:n_test_countries])

    test_mask = df["country"].isin(test_countries)
    train_mask = ~test_mask

    return {
        "train": df.index[train_mask].tolist(),
        "test": df.index[test_mask].tolist(),
        "strategy": "group_by_country",
        "test_countries": sorted(test_countries),
        "n_train": train_mask.sum(),
        "n_test": test_mask.sum(),
    }


def main():
    splits_manifest = {}

    # Lake Erie
    print("=== Lake Erie ===")
    erie_path = CLEANED_DIR / "erie_clean.pkl"
    if erie_path.exists():
        df_erie = pd.read_pickle(erie_path)
        split_erie = split_lake_erie(df_erie)
        splits_manifest["erie"] = split_erie
        print(f"  训练: {split_erie['n_train']}, 测试: {split_erie['n_test']}")
        print(f"  训练年份: {split_erie['train_years']}")
        print(f"  测试年份: {split_erie['test_years']}")

    # HABs Training
    print("\n=== HABs Training ===")
    habs_path = CLEANED_DIR / "habs_nla_clean.pkl"
    if habs_path.exists():
        df_habs = pd.read_pickle(habs_path)
        split_habs_data = split_habs(df_habs)
        splits_manifest["habs_nla"] = split_habs_data
        print(f"  训练: {split_habs_data['n_train']}, 测试: {split_habs_data['n_test']}")

    # EMLS (MC-LR)
    print("\n=== EMLS Europe (MC-LR) ===")
    emls_path = CLEANED_DIR / "emls_clean.pkl"
    if emls_path.exists():
        df_emls = pd.read_pickle(emls_path)
        split_emls_data = split_emls(df_emls)
        splits_manifest["emls"] = split_emls_data
        print(f"  训练: {split_emls_data['n_train']}, 测试: {split_emls_data['n_test']}")
        print(f"  测试国家: {split_emls_data['test_countries']}")

    # NCCA 2015 — used as external validation for EMLS model
    print("\n=== EPA NCCA 2015 (MC-LR 验证集) ===")
    ncca_path = CLEANED_DIR / "ncca2015_clean.pkl"
    if ncca_path.exists():
        df_ncca = pd.read_pickle(ncca_path)
        splits_manifest["ncca2015"] = {
            "strategy": "external_validation",
            "n_total": len(df_ncca),
            "note": "全量用于外部验证，不参与训练",
        }
        print(f"  全量验证: {len(df_ncca)} 行")

    # Save manifest
    manifest_path = SPLITS_DIR / "split_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(splits_manifest, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n划分清单已保存: {manifest_path}")


if __name__ == "__main__":
    main()
