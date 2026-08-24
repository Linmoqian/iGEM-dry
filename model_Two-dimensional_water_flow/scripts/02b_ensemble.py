# -*- coding: utf-8 -*-
"""Additional ensemble member spin-ups (wind uncertainty)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI
from swflow.swe_si import wind_stress
from swflow.viz import cell_velocities

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
dom = np.load(os.path.join(PROC, "domain.npz"))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])

def run_spinup(wind_mps, wind_dir, hours=24.0, dt=20.0, n=0.022, nu=0.5, label=""):
    cfg = SweConfigSI(dx=dx, dt=dt, n_manning=n, nu=nu, use_adv=True, use_coriolis=True, nu_mode='smag')
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    tau_x, tau_y, _cd = wind_stress(wind_mps, wind_dir, cd=cfg.c_d_wind)
    for _ in range(int(hours*3600.0/dt)):
        solver.step(st, tau_x, tau_y)
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2 + vc**2)
    print("%s: |u|max=%.4f mean=%.4f vol_drift=%.2e" % (label, float(sp[mask].max()), float(sp[mask].mean()), 0.0))
    return {"u": st["u"], "v": st["v"], "eta": st["eta"], "uc": uc, "vc": vc,
            "mask": mask, "depth": depth, "xs": xs, "ys": ys, "dx": dx,
            "wind_mps": wind_mps, "wind_dir": wind_dir, "label": label}

members = [(2.0, 120.0, "m0"), (3.0, 150.0, "m1"), (2.0, 150.0, "m2"), (3.0, 120.0, "m3")]
for spd, dirn, lab in members:
    res = run_spinup(spd, dirn, label=lab)
    np.savez_compressed(os.path.join(PROC, "flow_%s.npz" % lab), **res)
    print("saved", lab)
