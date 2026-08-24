# -*- coding: utf-8 -*-
"""E0c: does the B3 power-exponential bathymetry change circulation & coverage?
Compare 24 h SE 2.5 m/s spin-up + one particle release under depth A (current) vs depth B3.
B3 parameters: d = 4.66*(1-exp(-(dist/440)^0.39)), calibrated in 13_bathy_rbf.py.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from scipy.ndimage import distance_transform_edt
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI, wind_stress
from swflow.viz import cell_velocities
from swflow.deployment import sim_drop
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from swflow.viz import setup_style
setup_style()

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
_exp = os.path.join(PROC, "domain_exp.npz")
domA = dict(np.load(_exp if os.path.exists(_exp) else os.path.join(PROC, "domain.npz")))
domB = dict(np.load(os.path.join(PROC, "domain.npz")))
mask, xs, ys, dx = domB["mask"], domB["xs"], domB["ys"], float(domB["dx"])
dist = distance_transform_edt(mask) * dx
depthA = domA["depth"]   # legacy exponential baseline
depthB = np.where(mask, 4.66*(1.0 - np.exp(-np.power(dist/440.0, 0.39))), 0.0)

CFG = dict(dt=20.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode="smag")
Wind = (2.5, 135.0)
cfg = SweConfigSI(dx=dx, **CFG)
tau_x, tau_y, _ = wind_stress(*Wind, cd=cfg.c_d_wind)

def spin(depth, hours=24.0, label=""):
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    for _ in range(int(hours*3600.0/cfg.dt)):
        solver.step(st, tau_x, tau_y)
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2 + vc**2)
    print("%s: |u|max=%.4f mean=%.4f  (depth mean=%.2f max=%.2f)"
          % (label, float(sp[mask].max()), float(sp[mask].mean()), depth[mask].mean(), depth[mask].max()))
    return dict(u=st["u"], v=st["v"], eta=st["eta"], uc=uc, vc=vc, mask=mask, depth=depth,
                xs=xs, ys=ys, dx=dx, wind_mps=Wind[0], wind_dir=Wind[1], label=label)

fA = spin(depthA, label="A_exp")
fB = spin(depthB, label="B3_power")
# flow field difference
dU = np.sqrt((fB["uc"]-fA["uc"])**2 + (fB["vc"]-fA["vc"])**2)
print("flow |u| diff: mean=%.4f max=%.4f (of base mean %.4f)" % (dU[mask].mean(), dU[mask].max(), np.sqrt(fA["uc"]**2+fA["vc"]**2)[mask].mean()))

for lab, f in [("A", fA), ("B3", fB)]:
    res = sim_drop(f, (-1300.0, -200.0), T_h=2.0, dt=5.0, D=0.3, n=2500, sigma0=25.0, thr_rel=0.05, rng_seed=7)
    print("%s drop @(-1300,-200) 2h: area=%.4f km2  centroid=(%.0f,%.0f)  theta=%.1f"
          % (lab, res["area_km2"], res["centroid"][0], res["centroid"][1], res["theta"]))

np.savez_compressed(os.path.join(PROC, "flow_SE_2p5_bathyB3.npz"), **fB)
fig, axes = plt.subplots(1, 3, figsize=(18, 4.6))
spA = np.sqrt(fA["uc"]**2+fA["vc"]**2); spB = np.sqrt(fB["uc"]**2+fB["vc"]**2)
im = axes[0].pcolormesh(xs, ys, spB, cmap="viridis", shading="auto")
axes[0].set_title("B3 bathy: SE2.5 |u| max=%.3f" % spB[mask].max()); fig.colorbar(im, ax=axes[0], shrink=0.8)
im2 = axes[1].imshow(depthB, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap="YlGnBu")
axes[1].set_title("B3 depth (mean %.2f max %.2f)" % (depthB[mask].mean(), depthB[mask].max()))
fig.colorbar(im2, ax=axes[1], shrink=0.8)
im3 = axes[2].pcolormesh(xs, ys, dU, cmap="magma", shading="auto")
axes[2].set_title("|u| diff B3-A: mean=%.4f" % dU[mask].mean()); fig.colorbar(im3, ax=axes[2], shrink=0.8)
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig08_bathyB3_circulation_effect.png"), dpi=130)
print("saved fig08")
