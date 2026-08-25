# -*- coding: utf-8 -*-
"""dt-dependence of instability"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
from swflow.swe import ShallowWaterSolver, SweConfig, wind_stress
np.seterr(all='ignore')
mask = np.ones((50, 50), bool)
depth = np.full((50, 50), 2.3)
tau_x, tau_y = wind_stress(2.5, 135.0)
for dt in [2.0, 1.0, 0.5, 0.25]:
    cfg = SweConfig(dx=50.0, dt=dt, n_manning=0.022, nu=0.5, use_adv=False, use_coriolis=False)
    solver = ShallowWaterSolver(mask, depth, cfg)
    st = solver.init_state()
    blow_at = None
    for k in range(200000):
        solver.step(st, tau_x, tau_y)
        if not np.isfinite(st['eta']).all():
            blow_at = k*dt/3600.0
            break
    print('dt=%.2f blow_at=%.2f h (steps=%d)' % (dt, blow_at or -1, k if blow_at else 200000))
    if not blow_at:
        print('  eta_max=%.4f u_max=%.4f' % (np.abs(st['eta']).max(), np.abs(st['u']).max()))
