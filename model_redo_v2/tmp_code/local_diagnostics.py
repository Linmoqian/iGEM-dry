"""Local diagnostic experiments for CMADRE review rounds.

Reuses the real cmadre labels / features / splits modules (no xgboost/catboost needed)
and fits simple baselines plus a small censored Gaussian MLP with torch-CPU under the
same non-IID protocols the server uses. These numbers are DIAGNOSTIC evidence for
architecture review - not server benchmarks and not locked-test claims.

Outputs:
  references/review_local_experiments.json
  console summary
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cmadre.config import load_config  # noqa: E402
from cmadre.data import load_dataset  # noqa: E402
from cmadre.splits import make_split_manifest, split_indices, split_summary  # noqa: E402


def metrics_for(test_labels, pred, lo, hi) -> dict:
    exact = test_labels.exact
    y = test_labels.lower[exact]
    out = {}
    if len(y) > 0:
        yl = np.log1p(np.maximum(y, 0.0))
        pl = np.log1p(np.maximum(pred[exact], 0.0))
        mae = float(np.mean(np.abs(yl - pl)))
        spearman = (float(pd.Series(yl).corr(pd.Series(pl), method="spearman"))
                    if len(y) >= 3 else float("nan"))
        r2 = float(1 - np.sum((y - pred[exact]) ** 2) / (np.sum((y - y.mean()) ** 2) + 1e-12))
        f2 = float(np.mean((pred[exact] >= y / 2) & (pred[exact] <= y * 2)))
        medae = float(np.median(np.abs(y - pred[exact])))
        out = {"exact_count": int(len(y)), "log1p_mae": mae, "spearman": spearman,
               "r2": r2, "factor_of_2": f2, "median_ae_ug_l": medae}
        if len(y) >= 20:
            k = max(1, len(y) // 100)
            idx = np.argsort(-y)[:k]
            out["tail_top1pct_log1p_mae"] = float(
                np.mean(np.abs(np.log1p(y[idx]) - np.log1p(np.maximum(pred[exact][idx], 0.0)))))
    if lo is not None and hi is not None:
        yl = test_labels.lower
        yu = test_labels.upper
        exactm = test_labels.exact
        covered = float(np.mean((lo[exactm] <= yl[exactm]) & (hi[exactm] >= yu[exactm])))
        width = float(np.mean(hi - lo))
        compat = float(np.mean((lo <= yu) & (hi >= 0.0)))
        out["exact_coverage_q10_q90"] = covered
        out["avg_interval_width_ug_l"] = width
        out["interval_compatibility_all"] = compat
    return out


def median_imp_scale(Xtr, Xte):
    med = np.nanmedian(Xtr, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    scale = np.nanstd(Xtr, axis=0)
    scale = np.where(np.isfinite(scale) & (scale > 0), scale, 1.0)

    def prep(rows):
        m = np.isfinite(rows)
        filled = np.where(m, rows, med)
        return (filled - med) / scale

    return prep(Xtr), prep(Xte)


def train_censored_mlp(Xtr, lo_tr, hi_tr, ex_tr, Xva, lo_va, hi_va, ex_va, Xte_pred, seed=0):
    import torch
    import torch.nn as nn

    torch.manual_seed(seed + 7)
    np.random.seed(seed + 7)
    n_feat = Xtr.shape[1]
    Xtr_t = torch.tensor(Xtr, dtype=torch.float32)
    Xva_t = torch.tensor(Xva, dtype=torch.float32)
    Xte_arr_t = torch.tensor(Xte_pred, dtype=torch.float32)
    l_t = torch.tensor(np.log1p(np.maximum(lo_tr, 0.0)), dtype=torch.float32)
    u_t = torch.tensor(np.log1p(np.maximum(hi_tr, 0.0)), dtype=torch.float32)
    e_t = torch.tensor(ex_tr.astype(np.float32))
    vl_t = torch.tensor(np.log1p(np.maximum(lo_va, 0.0)), dtype=torch.float32)
    vu_t = torch.tensor(np.log1p(np.maximum(hi_va, 0.0)), dtype=torch.float32)
    ve_t = torch.tensor(ex_va.astype(np.float32))

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(n_feat, 256), nn.SiLU(), nn.Dropout(0.15),
                nn.Linear(256, 256), nn.SiLU(), nn.Dropout(0.15),
                nn.Linear(256, 128), nn.SiLU(), nn.Dropout(0.15),
            )
            self.mu = nn.Linear(128, 1)
            self.sc = nn.Linear(128, 1)

        def forward(self, x):
            h = self.net(x)
            mu = self.mu(h).squeeze(-1)
            sigma = 0.03 + (3.0 - 0.03) * torch.sigmoid(self.sc(h).squeeze(-1))
            return mu, sigma

    def nll(mu, sigma, lo, hi, exact):
        z = (lo - mu.double()) / sigma.double()
        density = torch.exp(-0.5 * z ** 2) / (sigma.double() * math.sqrt(2 * math.pi))
        z1 = (lo - mu.double()) / sigma.double()
        z2 = (hi - mu.double()) / sigma.double()
        phi1 = 0.5 * (1 + torch.erf(z1 / math.sqrt(2)))
        phi2 = 0.5 * (1 + torch.erf(z2 / math.sqrt(2)))
        interval = torch.clamp(phi2 - phi1, min=1e-12)
        exact_loss = -torch.log(torch.clamp(density, min=1e-12))
        interval_loss = -torch.log(interval)
        loss = torch.where(exact > 0.5, exact_loss, interval_loss).float().mean()
        return loss

    model = Net()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    n = Xtr_t.shape[0]
    best = (1e18, None)
    patience = 0
    for epoch in range(80):
        model.train()
        perm = torch.randperm(n)
        for i in range(0, n, 512):
            idx = perm[i:i + 512]
            mu, sigma = model(Xtr_t[idx])
            loss = nll(mu, sigma, l_t[idx], u_t[idx], e_t[idx])
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        model.eval()
        with torch.no_grad():
            mu, sigma = model(Xva_t)
        va = float(nll(mu, sigma, vl_t, vu_t, ve_t))
        if va < best[0] - 1e-5:
            best = (va, {k: v.clone() for k, v in model.state_dict().items()})
            patience = 0
        else:
            patience += 1
            if patience >= 12:
                break
    model.load_state_dict(best[1])
    model.eval()
    with torch.no_grad():
        mu, sigma = model(Xte_arr_t)
        qs = {}
        for q, z in (("q10", -1.2815515655), ("q50", 0.0), ("q90", 1.2815515655)):
            v = mu.double() + z * sigma.double()
            qs[q] = np.expm1(v.clamp(max=25).numpy())
    return qs


def run_task(overrides: dict) -> dict:
    config = load_config(None, overrides)
    view = load_dataset(config)
    manifest = make_split_manifest(view, config)
    idx = split_indices(manifest)
    feats = view.feature_names
    X = view.X[feats].astype(float)
    labels = view.labels

    tr_i, va_i, te_i = idx.train, idx.validation, idx.test
    summary = split_summary(manifest)

    Xtr_raw = X.iloc[tr_i].to_numpy(dtype=float)
    Xte_raw = X.iloc[te_i].to_numpy(dtype=float)
    Xva_raw = X.iloc[va_i].to_numpy(dtype=float)
    Xtr_p, Xte_p = median_imp_scale(Xtr_raw, Xte_raw)
    _, Xva_p = median_imp_scale(Xtr_raw, Xva_raw)

    mid = (labels.lower + labels.upper) / 2.0
    exact = labels.exact
    y_tr_mid_log = np.log1p(np.maximum(mid[tr_i], 0.0))

    results = {}

    # --- 1. Dummy median ---
    tr_median = float(np.median(y_tr_mid_log))
    dummy = np.full(len(te_i), np.expm1(tr_median))
    results["dummy_median"] = metrics_for(labels.subset(te_i), dummy, dummy, dummy)

    # --- 2. Source prior (unseen source -> global) ---
    src_tr = view.metadata.iloc[tr_i]["dataset_id"].astype(str).to_numpy()
    src_te = view.metadata.iloc[te_i]["dataset_id"].astype(str).to_numpy()
    prior = {s: float(np.mean(y_tr_mid_log[src_tr == s])) for s in np.unique(src_tr)}
    prior_pred = np.array([prior.get(s, tr_median) for s in src_te])
    results["source_prior"] = metrics_for(labels.subset(te_i), prior_pred, prior_pred, prior_pred)

    # --- 3. ElasticNet (log1p midpoints, censored downweighted) ---
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import ElasticNet
    imp = SimpleImputer(strategy="median").fit(Xtr_raw)
    w = np.where(exact[tr_i], 1.0, 0.25)
    en = ElasticNet(alpha=0.05, l1_ratio=0.5, max_iter=10000)
    en.fit(imp.transform(Xtr_raw), y_tr_mid_log, sample_weight=w)
    en_pred = np.expm1(en.predict(imp.transform(Xte_raw)))
    results["elasticnet_log1p"] = metrics_for(labels.subset(te_i), en_pred, en_pred, en_pred)

    # --- 4. RandomForest (log1p midpoints, censored downweighted) ---
    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=4, n_jobs=-1, random_state=42)
    rf.fit(imp.transform(Xtr_raw), y_tr_mid_log, sample_weight=w)
    rf_pred = np.expm1(rf.predict(imp.transform(Xte_raw)))
    results["random_forest"] = metrics_for(labels.subset(te_i), rf_pred, rf_pred, rf_pred)

    # --- 5. Censored Gaussian MLP ---
    try:
        qs = train_censored_mlp(Xtr_p, labels.lower[tr_i], labels.upper[tr_i], exact[tr_i],
                                Xva_p, labels.lower[va_i], labels.upper[va_i], exact[va_i], Xte_p)
        results["mlp_censored"] = metrics_for(labels.subset(te_i), qs["q50"], qs["q10"], qs["q90"])
    except Exception as exc:  # pragma: no cover
        results["mlp_censored"] = {"error": str(exc)}

    return {
        "config": config,
        "base": {
            "n_rows": len(X), "features": len(feats),
            "sources": int(view.metadata["dataset_id"].nunique()),
            "waterbodies": int(view.metadata["waterbody_group"].nunique()),
            "protocol": config["split_protocol"],
            "split_summary": summary,
            "test_rows": len(te_i),
            "exact_test": int(exact[te_i].sum()),
            "censored_test": int((~exact[te_i]).sum()),
        },
        "results": results,
    }


def main() -> None:
    out = {}
    out["total_mc_source_ood"] = run_task({
        "target": "total_microcystins", "panel": "core_field",
        "split_protocol": "source_ood", "n_folds": 5, "test_fold": 0, "validation_fold": 1,
        "minimum_feature_count": 3, "models": ["xgb_aft"],
    })
    out["mc_lr_waterbody_ood"] = run_task({
        "target": "mc_lr", "panel": "core_field",
        "split_protocol": "waterbody_ood", "n_folds": 5, "test_fold": 0, "validation_fold": 1,
        "minimum_feature_count": 3, "models": ["xgb_aft"],
    })
    OUT = ROOT / "references" / "review_local_experiments.json"
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    for task, rec in out.items():
        print("=" * 74)
        print(task, "| rows", rec["base"]["n_rows"], "| features", rec["base"]["features"],
              "| sources", rec["base"]["sources"], "| wb", rec["base"]["waterbodies"],
              "| protocol", rec["base"]["protocol"])
        print("split:", rec["base"]["split_summary"])
        print("test rows:", rec["base"]["test_rows"], "| exact", rec["base"]["exact_test"],
              "| censored", rec["base"]["censored_test"])
        for model, m in rec["results"].items():
            print(f"  {model:22s} -> {m}")


if __name__ == "__main__":
    main()
