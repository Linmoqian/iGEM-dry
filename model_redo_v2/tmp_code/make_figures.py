"""Generate the CMADRE report figures (English labels; Chinese captions live in the MD).

Outputs PNG to ../figures/:
  fig01_system_overview.png
  fig02_cmadre_architecture.png
  fig03_data_mix.png
  fig04_label_semantics.png
  fig05_local_diagnostics.png
  fig06_roadmap_priorities.png
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
audit = json.loads((ROOT / "references" / "review_data_audit.json").read_text(encoding="utf-8"))
diag = json.loads((ROOT / "references" / "review_local_experiments.json").read_text(encoding="utf-8"))

BG = "#f5f7fa"
BOX = "#ffffff"
EDGE = "#4a6785"
BLUE = "#2f6fb2"
GREEN = "#3a8f5f"
ORANGE = "#d97b29"
RED = "#b23a48"
GREY = "#8a97a6"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": EDGE,
    "axes.labelcolor": "#22303c",
    "text.color": "#22303c",
    "figure.facecolor": BG,
    "axes.facecolor": BOX,
    "savefig.facecolor": BG,
    "savefig.bbox": "tight",
    "axes.grid": True,
    "grid.color": "#d8e0e8",
    "grid.linewidth": 0.6,
})


def box(ax, x, y, w, h, text, fc=BOX, ec=EDGE, fs=9, weight="normal", dashed=False, tc="#22303c"):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.012",
                           linewidth=1.3, edgecolor=ec, facecolor=fc,
                           linestyle="--" if dashed else "-")
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            weight=weight, color=tc, wrap=True)
    return patch


def arrow(ax, p1, p2, color=EDGE, style="-|>", lw=1.4, conn="arc3,rad=0.0"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=11, lw=lw,
                        color=color, linestyle="-", connectionstyle=conn, shrinkA=3, shrinkB=3)
    ax.add_patch(a)


# ---------------------------------------------------------------- fig01
def fig01():
    fig, ax = plt.subplots(figsize=(13, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Closed loop: engineered-bacteria detection node, ML risk model and degradation UAV",
                 fontsize=12.5, weight="bold", pad=12)
    box(ax, 0.015, 0.68, 0.23, 0.24, "Floating detection node\nSTART riboswitch, Lux QS\nsfGFP/TurboRFP ratio", fc="#eaf3fb", ec=BLUE, fs=8.6)
    box(ax, 0.285, 0.68, 0.20, 0.24, "Raw measured signals\nfluorescence ratio,\nsensor LOD / batch", fc=BOX, fs=8.6)
    box(ax, 0.525, 0.68, 0.24, 0.24, "CMADRE v2\nnowcast total MC / MC-LR\nmedian + q10-q90 + OOD flag", fc="#eaf7ee", ec=GREEN, fs=8.6, weight="bold")
    box(ax, 0.805, 0.68, 0.18, 0.24, "Risk decision board\nWHO 1 ug/L threshold,\nsensor trigger", fc="#fdf2e7", ec=ORANGE, fs=8.6)
    box(ax, 0.015, 0.16, 0.23, 0.30, "Field covariates: water T, DO, pH,\nturbidity, conductivity, TN/TP,\nChl-a, LSWT + static climate /\nlandscape (remote sensing env.)", fc="#f2eef9", ec="#7a5fa8", fs=8.4)
    box(ax, 0.525, 0.16, 0.24, 0.30, "Training data: 20.8k total MC rows,\n2.8k MC-LR dynamic + 6.4k static rows\nsource / waterbody / temporal\nOOD splits", fc="#f0f4f8", ec=EDGE, fs=8.4)
    box(ax, 0.805, 0.16, 0.18, 0.30, "UAV dispatch of mlr-degrading\nbacteria + node replacement\n(future closed-loop control)", fc="#fdeef0", ec=RED, fs=8.4, dashed=True)
    arrow(ax, (0.245, 0.80), (0.285, 0.80))
    arrow(ax, (0.485, 0.80), (0.525, 0.80))
    arrow(ax, (0.765, 0.80), (0.805, 0.80))
    arrow(ax, (0.895, 0.68), (0.895, 0.46), color=RED)
    arrow(ax, (0.805, 0.31), (0.765, 0.31), color=RED)
    arrow(ax, (0.383, 0.68), (0.44, 0.46), conn="arc3,rad=-0.2")
    arrow(ax, (0.245, 0.30), (0.525, 0.32), color=GREEN)
    ax.text(0.505, 0.945, "sensing", color=BLUE, fontsize=8.5, ha="center")
    ax.text(0.665, 0.02, "future closed loop", color=RED, fontsize=8.5, ha="center")
    fig.savefig(FIG / "fig01_system_overview.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- fig02
def fig02():
    fig, ax = plt.subplots(figsize=(16, 10.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("CMADRE v2 architecture (solid = implemented/trained; dashed = designed, not yet in formal run)",
                 fontsize=13, weight="bold", pad=8)
    box(ax, 0.015, 0.865, 0.30, 0.11,
        "Model-ready tables\n(total MC dynamic/static; MC-LR dynamic/static)\nlabels [L,U], censoring flags, provenance", fc="#eaf3fb", ec=BLUE)
    box(ax, 0.335, 0.865, 0.30, 0.11,
        "Audit & leakage guard\nunit/matrix/method, forbidden columns,\nfeature whitelist (core / static / bloom)", fc="#eaf3fb", ec=BLUE)
    box(ax, 0.655, 0.865, 0.33, 0.11,
        "Non-IID split manifest\nsource-OOD | waterbody-OOD | temporal-OOD\ntrain / validation / locked test disjoint", fc="#eaf3fb", ec=BLUE)
    box(ax, 0.015, 0.615, 0.15, 0.15, "E1\nXGBoost AFT\ninterval-censored\n(offset-shift, normal)", fc="#ffffff", ec=BLUE)
    box(ax, 0.180, 0.615, 0.15, 0.15, "E2\nCatBoost / XGBoost\nquantile q10-q50-q90\n(midpoint, censor w=0.25)", fc="#ffffff", ec=BLUE)
    box(ax, 0.345, 0.615, 0.15, 0.15, "E2b\nXGBoost tail-quantile\ntrain-fold q90 high-weight\n(tail expert)", fc="#ffffff", ec=GREEN)
    box(ax, 0.510, 0.615, 0.15, 0.15, "E3\nTabM-inspired MiniEnsemble\ncensored Gaussian NLL\n(member adapters, shared MLP)", fc="#ffffff", ec=GREEN)
    box(ax, 0.675, 0.615, 0.15, 0.15, "E4 challenger\nTabICLv2 TFM\n(exact + multi-impute)\nnot in formal v2", fc="#f5f5f5", ec=GREY, dashed=True)
    box(ax, 0.840, 0.615, 0.145, 0.15, "Hurdle / detection head\np(detected)\ncoded, not in formal v2", fc="#f5f5f5", ec=GREY, dashed=True)
    box(ax, 0.180, 0.445, 0.52, 0.10, "OOF stacking (inside outer-train only)\nv2: non-negative NNLS on log1p(q50)\nv3 experiments: distributional objective (q10/q50/q90 pinball\n+ censored interval incompatibility + width penalty + L2)", fc="#eaf7ee", ec=GREEN, fs=8.4)
    box(ax, 0.720, 0.445, 0.26, 0.10, "Source-balanced weights\nprior 1/n_source, clipped [0.1, 10]\n(GroupDRO: not implemented)", fc="#fdf2e7", ec=ORANGE, fs=8.4)
    box(ax, 0.180, 0.300, 0.35, 0.09, "CQR conformal calibration\nexact-observation scores only, alpha=0.2,\nidentity or log1p transform", fc="#fdf2e7", ec=ORANGE, fs=8.4)
    box(ax, 0.555, 0.300, 0.35, 0.09, "OOD detector\nLedoit-Wolf Mahalanobis on median-imputed,\nrobust-scaled features + missing indicators", fc="#f2eef9", ec="#7a5fa8", fs=8.4)
    box(ax, 0.180, 0.155, 0.52, 0.11, "Outputs per sample\nmedian, q10-q90 calibrated interval, P(Y>tau) calculation,\nood_score / ood_flag, per-expert predictions, artifacts (hash, splits)", fc="#eaf7ee", ec=GREEN, fs=8.6)
    box(ax, 0.730, 0.155, 0.25, 0.11, "Future probability fusion\nsensor calibration model\n(concentration_calibration) x\nC(N_y|x) -> risk of true MC-LR", fc="#fdeef0", ec=RED, dashed=True, fs=8.4)
    box(ax, 0.180, 0.030, 0.52, 0.09, "Evaluation & honest reporting: log1p MAE, Spearman, R2, factor-of-2,\nworst-source macro avg, tail q90/q99, interval coverage/width, OOD rate", fc="#f0f4f8", ec=EDGE, fs=8.4)
    box(ax, 0.730, 0.030, 0.25, 0.09, "Deployment gates: simple-baseline\nbeat, repeated outer CV, Donghu\nlocal validation, threshold config", fc="#f0f4f8", ec=EDGE, fs=8.4)
    arrow(ax, (0.165, 0.865), (0.165, 0.77))
    arrow(ax, (0.485, 0.865), (0.485, 0.77))
    arrow(ax, (0.655, 0.865), (0.76, 0.77))
    for x in (0.09, 0.255, 0.42, 0.585, 0.75):
        arrow(ax, (x, 0.615), (x, 0.55))
    arrow(ax, (0.70, 0.445), (0.72, 0.445))
    arrow(ax, (0.36, 0.445), (0.36, 0.40))
    arrow(ax, (0.73, 0.445), (0.73, 0.40))
    arrow(ax, (0.44, 0.30), (0.44, 0.27))
    arrow(ax, (0.73, 0.30), (0.73, 0.27))
    ax.text(0.5, 0.79, "same outer-train only (no test peek)", fontsize=8, color=GREY, ha="center")
    fig.savefig(FIG / "fig02_cmadre_architecture.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- fig03
def fig03():
    tm = audit["total_microcystins_enriched_dynamic_ready.csv"]
    ml = audit["mc_lr_enriched_dynamic_ready.csv"]
    ms = audit["mc_lr_enriched_static_baseline_ready.csv"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    srcs = sorted(tm["source_counts"].items(), key=lambda kv: -kv[1])
    ax.barh(range(len(srcs)), [v for _, v in srcs], color=BLUE, height=0.62)
    ax.set_yticks(range(len(srcs)))
    ax.set_yticklabels([k[:26] for k, _ in srcs], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_title("Total MC dynamic-ready: rows per source (n=20,852)", fontsize=10)
    ax.set_xlabel("rows")
    ax = axes[1]
    srcs = sorted(ml["source_counts"].items(), key=lambda kv: -kv[1])
    ax.barh(range(len(srcs)), [v for _, v in srcs], color=GREEN, height=0.5)
    ax.set_yticks(range(len(srcs)))
    ax.set_yticklabels([k[:30] for k, _ in srcs], fontsize=8)
    ax.invert_yaxis()
    ax.set_title("MC-LR dynamic-ready (n=2,837; 100% detected)", fontsize=10)
    ax.set_xlabel("rows")
    ax = axes[2]
    srcs = sorted(ms["source_counts"].items(), key=lambda kv: -kv[1])
    ax.barh(range(len(srcs)), [v for _, v in srcs], color=ORANGE, height=0.55)
    ax.set_yticks(range(len(srcs)))
    ax.set_yticklabels([k[:30] for k, _ in srcs], fontsize=8)
    ax.invert_yaxis()
    ax.set_title("MC-LR static-ready (n=6,409; 3,417 censored)", fontsize=10)
    ax.set_xlabel("rows")
    fig.tight_layout()
    fig.savefig(FIG / "fig03_data_mix.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- fig04
def fig04():
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.4))
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.97, "Label encoding: interval [L, U] in ug/L (log scale)", fontsize=10, ha="center", weight="bold")
    ax.plot([0.10, 0.42], [0.80, 0.80], color=EDGE, lw=2)
    ax.plot(0.10, 0.80, "o", color=BLUE, ms=7)
    ax.text(0.10, 0.86, "exact: L=U=y", fontsize=8.5, ha="center")
    ax.plot([0.55, 0.90], [0.60, 0.60], color=EDGE, lw=2)
    ax.plot([0.55, 0.90], [0.52, 0.52], color=RED, lw=1)
    ax.plot(0.90, 0.60, "o", color=BLUE, ms=7)
    ax.text(0.72, 0.64, "left-censored [0, LOD]", fontsize=8.5, ha="center")
    ax.text(0.72, 0.44, "midpoint (LOD/2) = transparent\napproximation, NOT the label", fontsize=8.5, ha="center", color=RED)
    ax.plot([0.10, 0.55], [0.24, 0.24], color=BLUE, lw=2)
    ax.text(0.33, 0.16, "interval-censored (component sums):\n[L,U] from intracellular + extracellular", fontsize=8.5, ha="center")
    ax.text(0.5, 0.03, "exact zeros audited separately: 321 total MC / 319 MC-LR", fontsize=8, ha="center", color=GREY)
    ax = axes[1]
    import pandas as pd
    d1 = pd.read_csv(ROOT / "data/model_tables/total_microcystins_enriched_dynamic_ready.csv", usecols=["target_ug_l", "is_censored"], low_memory=False)
    d2 = pd.read_csv(ROOT / "data/model_tables/mc_lr_enriched_dynamic_ready.csv", usecols=["target_ug_l", "is_censored"], low_memory=False)
    v1 = d1.loc[(~d1["is_censored"].fillna(0).astype(bool)), "target_ug_l"]
    v2 = d2.loc[(~d2["is_censored"].fillna(0).astype(bool)), "target_ug_l"]
    bins = np.logspace(-3, 5, 42)
    ax.hist(np.clip(v1, 1e-3, 1e5), bins=bins, alpha=0.65, label="total MC exact (n=9,528)", color=BLUE)
    ax.hist(np.clip(v2, 1e-3, 1e5), bins=bins, alpha=0.65, label="MC-LR exact (n=2,837)", color=GREEN)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("exact concentration (ug/L, log)")
    ax.set_ylabel("count (log)")
    ax.set_title("Exact label distributions", fontsize=10)
    ax.legend(fontsize=7.5)
    ax = axes[2]
    d1m = pd.read_csv(ROOT / "data/model_tables/total_microcystins_enriched_dynamic_ready.csv", usecols=["censor_limit_ug_l", "dataset_id"], low_memory=False)
    d2m = pd.read_csv(ROOT / "data/model_tables/mc_lr_enriched_static_baseline_ready.csv", usecols=["censor_limit_ug_l", "dataset_id"], low_memory=False)
    data = []
    for name, d in (("total MC\n(11,324 censored)", d1m), ("MC-LR static\n(3,417 censored)", d2m)):
        v = pd.to_numeric(d["censor_limit_ug_l"], errors="coerce").dropna()
        data.append(np.clip(v, 1e-3, 10))
    bp = ax.boxplot(data, tick_labels=["total MC", "MC-LR static"], widths=0.5, showfliers=False, patch_artist=True)
    for patch, color in zip(bp["boxes"], [BLUE, ORANGE]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_yscale("log")
    ax.set_ylabel("censor limit / LOD (ug/L, log)")
    ax.set_title("Detection limits used for censored records", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "fig04_label_semantics.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- fig05
def fig05():
    total = diag["total_mc_source_ood"]["results"]
    mclr = diag["mc_lr_waterbody_ood"]["results"]
    servers = {"total_mc_source_ood": {"v2_ensemble": 0.3488, "v2_spearman": 0.3190, "v2_f2": 0.3811, "v2_median_ae": 0.1470},
               "mc_lr_waterbody_ood": {"v2_ensemble": 0.2972, "v2_spearman": 0.5091, "v2_f2": 0.5408, "v2_median_ae": 0.1029}}
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    order = ["dummy_median", "source_prior", "elasticnet_log1p", "random_forest", "mlp_censored"]
    labels = ["Dummy median", "Source prior\n(midpoints)", "ElasticNet\n(log1p)", "RandomForest\n(300 trees)", "Censored MLP\n(local proxy)"]
    colors = [GREY, GREY, ORANGE, BLUE, GREEN]
    for idx, (metric, title, ylabel, ax) in enumerate([
        ("log1p_mae", "log1p MAE on exact test labels (lower better)", "log1p MAE", axes[0]),
        ("factor_of_2", "factor-of-2 rate (higher better)", "factor-of-2", axes[1]),
        ("tail_top1pct_log1p_mae", "top-1% true-concentration tail log1p MAE (lower better)", "tail log1p MAE", axes[2]),
    ]):
        vals_t = [total[m].get(metric, float("nan")) for m in order]
        vals_m = [mclr[m].get(metric, float("nan")) for m in order]
        x = np.arange(len(order))
        ax.bar(x - 0.19, vals_t, 0.36, color=colors, alpha=0.9, label="total MC (source OOD)")
        ax.bar(x + 0.19, vals_m, 0.36, color=colors, alpha=0.55, hatch="//", label="MC-LR (waterbody OOD)")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=7.4)
        ax.set_title(title, fontsize=9.5)
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=7)
    axes[0].axhline(servers["total_mc_source_ood"]["v2_ensemble"], color=RED, ls="--", lw=1.2,
                     label="server v2 ensemble: total MC")
    axes[0].axhline(servers["mc_lr_waterbody_ood"]["v2_ensemble"], color=RED, ls=":", lw=1.2,
                    label="server v2 ensemble: MC-LR")
    axes[0].legend(fontsize=6.8, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "fig05_local_diagnostics.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- fig06
def fig06():
    fig, ax = plt.subplots(figsize=(14, 5.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Priority roadmap (P0 = before further locked-test claims; P1 = next statistical upgrades; P2 = needs new data)",
                 fontsize=12, weight="bold", pad=8)
    box(ax, 0.015, 0.62, 0.30, 0.30, "P0 gates\n- freeze v2 + hashes\n- same-split baselines (Dummy/source prior/ElasticNet/RF)\n- repeated outer CV (source/waterbody/seed)\n- extreme-value audit (>1000 ug/L, unit, matrix)\n- tail + risk-threshold metrics; Brier/ECE/decision curve",
        fc="#fdeef0", ec=RED, fs=8.2, weight="bold")
    box(ax, 0.355, 0.62, 0.30, 0.30, "P1 statistical upgrades\n- censored-aware stacking (interval score not midpoint)\n- tail-aware mixture head (log-normal + extreme component)\n- coherent distribution ensemble (CRPS/NLL)\n- Mondrian/weighted conformal by source, season\n- interpretable OOD + domain classifier (425k China covariates)\n- multi-task transfer ablation (only if worst-source improves)",
        fc="#fdf2e7", ec=ORANGE, fs=8.2, weight="bold")
    box(ax, 0.695, 0.62, 0.29, 0.30, "P2 data-dependent\n- MC-LR LC-MS/MS exact + LOD by lake/season (Donghu!)\n- strict-lag met/hydro/LSWT/RS + toxin time series\n- sensor calibration & batch drift model\n- biological: mlr gene/toxin-cell quota models\n- hourly nowcast + 1/3/7-day forecast with rolling origin",
        fc="#eaf3fb", ec=BLUE, fs=8.2, weight="bold")
    ax.text(0.165, 0.55, "evidence-based", fontsize=8, ha="center", color=RED)
    ax.text(0.505, 0.55, "architecture-driven", fontsize=8, ha="center", color=ORANGE)
    ax.text(0.84, 0.55, "data-driven", fontsize=8, ha="center", color=BLUE)
    box(ax, 0.015, 0.20, 0.98, 0.26,
        "What NOT to do next\n- do not swap in bigger transformers / GNN / TabPFN-3 while non-IID gains are unproven\n- do not use locked test to re-select weights or hyperparameters\n- do not pseudo-label the 425k China covariates as toxin values\n- do not merge ELISA total-MC / ADDA-ELISA equivalents with congener-specific LC-MS/MS MC-LR\n- do not treat bloom proxies as synchronous deployment inputs in the core model",
        fc="#f5f5f5", ec=GREY, fs=8.4)
    fig.savefig(FIG / "fig06_roadmap_priorities.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    fig01()
    fig02()
    fig03()
    fig04()
    fig05()
    fig06()
    print("figures written to", FIG)
