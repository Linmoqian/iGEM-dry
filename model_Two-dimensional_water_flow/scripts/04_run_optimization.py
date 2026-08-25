# -*- coding: utf-8 -*-
"""Drone drop-point optimization under wind uncertainty (ensemble of flow fields)."""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.deployment import sim_drop, batch_sim_drops, bloom_patch, physical_thr_rel
from swflow.viz import setup_style
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--thr", type=float, default=0.05,
                help="relative coverage threshold (demo 0.05; use --thr physical e.g. "
                     "0.25 or omit and let --physical resolve from C0/t_ok/T/M)")
ap.add_argument("--physical", action="store_true",
                help="resolve thr_rel = physical_thr_rel(C0, t_ok, T_water, M) instead of --thr")
ap.add_argument("--C0", type=float, default=2.85)
ap.add_argument("--t_ok", type=float, default=24.0)
ap.add_argument("--T_water", type=float, default=25.0)
ap.add_argument("--M", type=float, default=1.0)
ap.add_argument("--out", default="opt_result.npz", help="output filename under data/processed")
args = ap.parse_args()
THR = physical_thr_rel(args.C0, args.t_ok, args.T_water, args.M) if args.physical else float(args.thr)
print("thr_rel = %.4f (%s)" % (THR, "physical C0=%.2f/t_ok=%.0fh/T=%.0fC/M=%.1f" % (args.C0, args.t_ok, args.T_water, args.M)
                              if args.physical else "--thr given"))
ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
setup_style()

# ensemble members: deterministic perturbation of baseline SE wind
labels = ["m0", "SE_2p5", "m1", "m2", "m3"]   # 2.0/120, 2.5/135, 3.0/150, 2.0/150, 3.0/120
flows = []
use_real = all(os.path.exists(os.path.join(PROC, "flow_%s.npz" % lab)) for lab in labels)
if use_real:
    for lab in labels:
        f = np.load(os.path.join(PROC, "flow_%s.npz" % lab))
        flows.append(dict(f))
else:
    # fallback (documented): linear wind-scaling of the baseline flow
    members = [(2.0, 120.0), (2.5, 135.0), (3.0, 150.0), (2.0, 150.0), (3.0, 120.0)]
    f = np.load(os.path.join(PROC, "flow_SE_2p5.npz"))
    base = float(f["wind_mps"])
    for spd, d_ in members:
        ff = dict(f)
        scale = (spd/base)**2.0
        ff["uc"] = ff["uc"]*scale
        ff["vc"] = ff["vc"]*scale
        ff["wind_mps"] = spd; ff["wind_dir"] = d_
        flows.append(ff)
print("ensemble members:", len(flows))

flow0 = flows[1]
xs, ys, dx = flow0["xs"], flow0["ys"], float(flow0["dx"])
mask = flow0["mask"]
# target bloom patch: ellipse near western (Guozheng) basin center
patch = bloom_patch(mask, xs, ys, cx=-1300.0, cy=-200.0, rx=900.0, ry=500.0, theta_deg=20.0)
print("bloom patch area: %.2f km2" % (patch.sum()*dx*dx/1e6))

# candidates: wet cells every 4 cells (200 m)
jj, ii = np.where(mask)
sel = (ii % 4 == 0) & (jj % 4 == 0)
cands = np.column_stack([(xs[ii[sel]]), (ys[jj[sel]])])
print("candidates:", len(cands))

T_h = 1.5
scores = []
for fi, f in enumerate(flows):
    outs = batch_sim_drops(f, cands, T_h=T_h, dt=10.0, D=0.3, n=600, sigma0=25.0, thr_rel=THR)
    s = []
    for (area, cxy, C, cov) in outs:
        inter = (cov & patch).sum()
        frac = float(inter)/max(1.0, patch.sum())
        s.append(frac)
    scores.append(np.array(s))
    print("member %d done, mean frac %.4f max %.4f" % (fi, np.mean(s), np.max(s)))
S = np.mean(scores, axis=0)
order = np.argsort(-S)
print("top5 candidates:")
import numpy as _np
Sarr = _np.array(scores)
for k in order[:5]:
    print("  cand (%.0f,%.0f): expected frac=%.3f  (members:%s)"
          % (cands[k, 0], cands[k, 1], S[k], _np.round(Sarr[:, k], 3)))

np.savez_compressed(os.path.join(PROC, args.out), cands=cands, scores=S,
                    member_scores=np.array(scores), patch=patch, thr_rel=THR,
                    thr_kind=("physical" if args.physical else "demo"))

# figure
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
ax = axes[0]
sc = ax.scatter(cands[:, 0], cands[:, 1], c=S, cmap="RdYlGn", s=28, edgecolors="none")
ax.contour(xs, ys, patch.astype(float), levels=[0.5], colors="k", linewidths=1.6)
best = order[0]
ax.scatter(cands[best, 0], cands[best, 1], c="blue", s=180, marker="*", label="best drop")
for k in order[1:5]:
    ax.scatter(cands[k, 0], cands[k, 1], c="blue", s=70, marker="+", alpha=0.7)
ax.set_title("expected protected bloom fraction per drop point (T=%.1f h, 5-member ensemble)" % T_h)
ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
fig.colorbar(sc, ax=ax, shrink=0.85, label="expected fraction")
ax.legend()
# coverage of best candidate under each member
ax2 = axes[1]
for fi, f in enumerate(flows):
    outs = batch_sim_drops(f, cands[[best]], T_h=T_h, dt=10.0, D=0.3, n=2000, sigma0=25.0, thr_rel=THR)
    area, cxy, C, cov = outs[0]
    ax2.contour(xs, ys, C, levels=[THR*np.max(C)], colors=["tab:red"], linewidths=1.4)
    ax2.contour(xs, ys, patch.astype(float), levels=[0.5], colors="k", linewidths=1.2, linestyles="--")
    ax2.scatter([cands[best, 0]], [cands[best, 1]], c="b", s=80, marker="*")
ax2.set_title("best drop: coverage contour per member (red) vs bloom patch (black)")
ax2.set_xlabel("x (m)")
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig04_optimization.png"), dpi=130)
print("saved fig04")
