# -*- coding: utf-8 -*-
"""Debug NaN onset in SWE on real domain."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
from swflow.swe import ShallowWaterSolver, SweConfig, wind_stress
PROC = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
dom = np.load(os.path.join(PROC, 'domain.npz'))
mask, depth, xs, ys, dx = dom['mask'], dom['depth'], dom['xs'], dom['ys'], float(dom['dx'])
np.seterr(all='ignore')
cfg = SweConfig(dx=dx, dt=2.0, n_manning=0.022, nu=0.5)
solver = ShallowWaterSolver(mask, depth, cfg)
st = solver.init_state()
tau_x, tau_y = wind_stress(2.5, 135.0)
for k in range(300):
    solver.step(st, tau_x, tau_y)
    eta = st['eta']; u = st['u']; v = st['v']
    bad = np.argwhere(~np.isfinite(eta)) | np.argwhere(~np.isfinite(u)) 
    n_eta = int((~np.isfinite(eta)).sum()); n_u = int((~np.isfinite(u)).sum()); n_v = int((~np.isfinite(v)).sum())
    if n_eta or n_u or n_v:
        print('NaN at step', k, 'eta_nan', n_eta, 'u_nan', n_u, 'v_nan', n_v)
        idx = np.argwhere(~np.isfinite(u))
        print('first u NaN at', idx[0] if len(idx) else None)
        break
    if k in (5, 20, 50, 100, 200, 299):
        print('step', k, 'eta max %.3e u max %.3e v max %.3e' % (np.abs(eta).max(), np.abs(u).max(), np.abs(v).max()))
