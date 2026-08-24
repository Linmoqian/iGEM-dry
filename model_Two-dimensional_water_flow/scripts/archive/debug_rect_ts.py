# -*- coding: utf-8 -*-
"""Rect basin time series: growth pattern + 1D channel sanity check"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
from swflow.swe import ShallowWaterSolver, SweConfig, wind_stress
np.seterr(all='ignore')

mask = np.ones((50, 50), bool)
depth = np.full((50, 50), 2.3)
cfg = SweConfig(dx=50.0, dt=2.0, n_manning=0.022, nu=0.5, use_adv=False, use_coriolis=False)
solver = ShallowWaterSolver(mask, depth, cfg)
st = solver.init_state()
tau_x, tau_y = wind_stress(2.5, 135.0)
print('tau =', tau_x, tau_y)
for k in range(6000):
    solver.step(st, tau_x, tau_y)
    if k % 500 == 0:
        print('t=%.2fh eta_max=%.4f u_max=%.4f u_mean=%.4f' % (k*2/3600, np.abs(st['eta']).max(), np.abs(st['u']).max(), st['u'].mean()))
    if not np.isfinite(st['eta']).all():
        print('BLOW at', k); break
