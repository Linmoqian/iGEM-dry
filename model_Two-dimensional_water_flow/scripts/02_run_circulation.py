# -*- coding: utf-8 -*-
"""Spin up wind-driven circulation (semi-implicit solver) and save flow fields."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI
from swflow.swe_si import wind_stress
from swflow.viz import setup_style, cell_velocities
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
setup_style()

dom = np.load(os.path.join(PROC, "domain.npz"))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])
print("domain", mask.shape, "wet", int(mask.sum()), file=sys.stderr)

def run_spinup(wind_mps, wind_dir, hours=36.0, dt=20.0, n=0.0238, nu=0.5, label=""):
    cfg = SweConfigSI(dx=dx, dt=dt, n_manning=n, nu=nu, use_adv=True, use_coriolis=True,
                      nu_mode='smag', cs=0.29)   # Smagorinsky 0.29 = MIKE21 Donghu calibration
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    tau_x, tau_y, cd_used = wind_stress(wind_mps, wind_dir, cd_mode=cfg.cd_mode)  # 'lake' default
    nsteps = int(hours*3600.0/dt)
    trace = []
    vol0 = solver.volume(st)
    for k in range(nsteps):
        solver.step(st, tau_x, tau_y)
        if k % (nsteps//12) == 0:
            uc, vc = cell_velocities(st)
            sp = np.sqrt(uc**2 + vc**2)[mask]
            trace.append((k*dt/3600.0, float(sp.max()), float(sp.mean())))
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2 + vc**2)
    vol_drift = abs(solver.volume(st)-vol0)/vol0
    print("%s wind=%.1f m/s from %d deg: |u|max=%.4f mean=%.4f vol_drift=%.2e (Cd=%.4g mode=%s)"
          % (label, wind_mps, wind_dir, float(sp[mask].max()), float(sp[mask].mean()), vol_drift,
             cd_used, cfg.cd_mode), file=sys.stderr)
    return {"u": st["u"], "v": st["v"], "eta": st["eta"], "uc": uc, "vc": vc,
            "mask": mask, "depth": depth, "xs": xs, "ys": ys, "dx": dx,
            "trace": np.array(trace), "wind_mps": wind_mps, "wind_dir": wind_dir,
            "cd_used": cd_used, "cd_mode": cfg.cd_mode, "n_manning": n, "label": label}

cases = [
    ("SE_2p5", 2.5, 135.0),
    ("N_3p0", 3.0, 0.0),
    ("W_2p0", 2.0, 270.0),
]
results = []
for label, spd, dirn in cases:
    res = run_spinup(spd, dirn, label=label)
    np.savez_compressed(os.path.join(PROC, "flow_%s.npz" % label), **res)
    results.append(res)

# figure: 3 flow panels
fig, axes = plt.subplots(1, 3, figsize=(19, 5.2))
for ax, res in zip(axes, results):
    sp = np.sqrt(res["uc"]**2 + res["vc"]**2)
    im = ax.pcolormesh(res["xs"], res["ys"], sp, cmap="viridis", shading="auto")
    x2, y2 = np.meshgrid(res["xs"], res["ys"])
    step = 6
    ax.quiver(x2[::step, ::step], y2[::step, ::step], res["uc"][::step, ::step], res["vc"][::step, ::step],
              width=0.0022, scale=60, color="w")
    ax.set_title("%s: wind %.1f m/s from %d deg (36h), max=%.3f m/s"
                 % (res["label"], res["wind_mps"], res["wind_dir"], float(sp[res["mask"]].max())))
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
fig.colorbar(im, ax=axes, shrink=0.85, label="speed (m/s)")
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig02_circulation_3scenarios.png"), dpi=130)
print("saved fig02")
