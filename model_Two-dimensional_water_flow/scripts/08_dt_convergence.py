# -*- coding: utf-8 -*-
"""V5: dt-convergence test on the real domain (1h spin-up each)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI
from swflow.swe_si import wind_stress
PROC = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
dom = np.load(os.path.join(PROC, "domain.npz"))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])
fields = {}
for dt in [10.0, 20.0, 40.0]:
    cfg = SweConfigSI(dx=dx, dt=dt, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode='smag')
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    tx, ty, _cd = wind_stress(2.5, 135.0)
    for _ in range(int(3600.0/dt)):
        solver.step(st, tx, ty)
    fields[dt] = st
    print("dt=%.0f done" % dt)
ref = fields[10.0]
for dt in [10.0, 20.0, 40.0]:
    if dt == 10.0: continue
    rms_u = np.sqrt(np.mean((fields[dt]["u"] - ref["u"])**2))
    rms_eta = np.sqrt(np.mean((fields[dt]["eta"] - ref["eta"])**2))
    print("vs dt=10: dt=%.0f -> rms(u)=%.5f m/s rms(eta)=%.6f m" % (dt, rms_u, rms_eta))
