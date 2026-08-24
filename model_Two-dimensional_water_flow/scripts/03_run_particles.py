# -*- coding: utf-8 -*-
"""Single-drop dispersion & coverage experiments (may take a few minutes)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.particles import ParticleTracer
from swflow.deployment import sim_drop
from swflow.viz import setup_style
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
setup_style()

def load_flow(label):
    d = np.load(os.path.join(PROC, "flow_%s.npz" % label))
    return dict(d)

flow = load_flow("SE_2p5")
xs, ys = flow["xs"], flow["ys"]
# drop points in grid coords (cell indices) - mid-lake spots
# pick by x/y
pts = [(0.0, 1500.0), (-2500.0, -500.0), (2500.0, 1500.0)]
dx = float(flow["dx"])
print("testing drop points:", pts)
res_all = []
for (px, py) in pts:
    res = sim_drop(flow, (px, py), T_h=2.0, dt=5.0, D=0.3, n=2500, sigma0=25.0, thr_rel=0.05, record=True)
    print("drop at (%.0f, %.0f): area=%.3f km2 centroid=(%.0f, %.0f) eig=%.0f/%.0f theta=%.1f deg"
          % (px, py, res["area_km2"], res["centroid"][0], res["centroid"][1],
             np.sqrt(res["eig_var"][0]), np.sqrt(res["eig_var"][1]), res["theta"] or 0))
    res_all.append((px, py, res))

# coverage vs time curve for the central drop
res_t = []
for T in [0.25, 0.5, 1.0, 1.5, 2.0, 3.0]:
    r = sim_drop(flow, (0.0, 1500.0), T_h=T, dt=5.0, D=0.3, n=2500, sigma0=25.0, thr_rel=0.05)
    res_t.append((T, r["area_km2"]))
print("coverage vs time:", res_t)

fig, axes = plt.subplots(1, 3, figsize=(18, 5.4))
ax = axes[0]
sp = np.sqrt(flow["uc"]**2 + flow["vc"]**2)
ax.pcolormesh(xs, ys, sp, cmap="viridis", shading="auto")
for (px, py, res) in res_all:
    ax.plot(res["traj"][0][:, 0], res["traj"][0][:, 1], "r.", ms=1.5, alpha=0.5)
    ax.plot(res["pos_end"][:, 0], res["pos_end"][:, 1], "y.", ms=2, alpha=0.7)
ax.set_title("SE 2.5 m/s flow + 3 single drops (red=release, yellow=after 2h)")
ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
ax2 = axes[1]
C = res_all[1][2]["C"]
ax2.pcolormesh(xs, ys, C, cmap="magma", shading="auto")
ax2.set_title("droplet field after 2h (2nd drop), coverage=%.2f km2" % res_all[1][2]["area_km2"])
ax2.set_xlabel("x (m)")
ax3 = axes[2]
ts = [t for t, _ in res_t]; ar = [a for _, a in res_t]
ax3.plot(ts, ar, "o-")
ax3.set_title("coverage area vs time (thr=5% of peak)")
ax3.set_xlabel("t (h)"); ax3.set_ylabel("coverage km^2")
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig03_drops_coverage.png"), dpi=130)
print("saved fig03")
