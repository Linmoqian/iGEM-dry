# -*- coding: utf-8 -*-
"""Sensitivity: wind scenario, threshold, Manning, viscosity effects on coverage."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI
from swflow.swe_si import wind_stress
from swflow.deployment import sim_drop
from swflow.viz import setup_style, cell_velocities
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
setup_style()

def load_flow(label):
    return dict(np.load(os.path.join(PROC, "flow_%s.npz" % label)))

P0 = (0.0, 1500.0)
# (1) wind scenario effect on coverage
rows = []
for lab in ["SE_2p5", "N_3p0", "W_2p0"]:
    f = load_flow(lab)
    r = sim_drop(f, P0, T_h=2.0, dt=5.0, D=0.3, n=2000, sigma0=25.0, thr_rel=0.05)
    rows.append((lab, f["wind_mps"], f["wind_dir"], r["area_km2"]))
    print("scenario", lab, "coverage %.4f km2" % r["area_km2"])

# (2) threshold curve from one run
f = load_flow("SE_2p5")
r = sim_drop(f, P0, T_h=2.0, dt=5.0, D=0.3, n=2000, sigma0=25.0, thr_rel=0.05)
C = r["C"]; dx = float(f["dx"])
thr_areas = []
for thr in [0.005, 0.01, 0.05, 0.10, 0.20, 0.50]:
    cov = (C >= thr*r["peak0"]) & f["mask"]
    thr_areas.append((thr, float(cov.sum()*dx*dx/1e6)))
print("threshold curve:", thr_areas)

# (3) Manning sensitivity: quick 12h spin-ups
manning_rows = []
for n_ in [0.015, 0.030]:
    dom = np.load(os.path.join(PROC, "domain.npz"))
    mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])
    cfg = SweConfigSI(dx=dx, dt=20.0, n_manning=n_, nu=0.5, use_adv=True, use_coriolis=True, nu_mode='smag')
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    tx, ty, _cd = wind_stress(2.5, 135.0)
    for _ in range(int(12*3600/20.0)):
        solver.step(st, tx, ty)
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2+vc**2)
    print("Manning %.3f: |u|max=%.4f mean=%.4f" % (n_, float(sp[mask].max()), float(sp[mask].mean())))
    rr = sim_drop({"uc": uc, "vc": vc, "mask": mask, "xs": xs, "ys": ys, "dx": dx},
                  P0, T_h=2.0, dt=5.0, D=0.3, n=2000, sigma0=25.0, thr_rel=0.05)
    print("Manning %.3f coverage %.4f km2" % (n_, rr["area_km2"]))
    manning_rows.append((n_, float(sp[mask].max()), rr["area_km2"]))
# baseline n = 0.0238 from the SE scenario run
f0 = load_flow('SE_2p5')
sp0 = np.sqrt(f0['uc']**2 + f0['vc']**2)
manning_rows.append((0.0238, float(sp0[f0['mask']].max()), rows[0][3]))

# figure
fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
ax = axes[0]
labels = [r[0] for r in rows]; vals = [r[3] for r in rows]
ax.bar(labels, vals, color=["#3182ce", "#e53e3e", "#2f855a"])
ax.set_title("coverage vs wind scenario (2 h, thr=5%)")
ax.set_ylabel("km2")
ax2 = axes[1]
ax2.plot([t*100 for t, a in thr_areas], [a for t, a in thr_areas], "o-")
ax2.set_xscale("log")
ax2.set_title("coverage vs threshold")
ax2.set_xlabel("thr (% of peak)"); ax2.set_ylabel("km2")
ax3 = axes[2]
ns = [m[0] for m in manning_rows]; spped = [m[1] for m in manning_rows]; covs = [m[2] for m in manning_rows]
ax3.bar(["%.3f" % n for n in ns], covs, color="#2f855a", alpha=0.85)
ax3.set_title("coverage vs Manning n (12h spin-up)")
ax3.set_xlabel("Manning n"); ax3.set_ylabel("coverage km2")
for x, v in zip(range(len(ns)), covs):
    ax3.text(x, v + 0.001, "%.3f" % v, ha="center", fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig05_sensitivity.png"), dpi=130)
print("saved fig05")
