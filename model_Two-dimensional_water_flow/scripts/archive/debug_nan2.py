# -*- coding: utf-8 -*-
"""Find when/where NaN appears and inspect the cell."""
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
for k in range(60*3600//2):
    solver.step(st, tau_x, tau_y)
    eta = st['eta']; u = st['u']; v = st['v']
    n_eta = int((~np.isfinite(eta)).sum()); n_u = int((~np.isfinite(u)).sum()); n_v = int((~np.isfinite(v)).sum())
    if n_eta or n_u or n_v:
        print('NaN at step', k, 't=%.1f min' % (k*2/60), 'eta', n_eta, 'u', n_u, 'v', n_v)
        idx = np.argwhere(~np.isfinite(eta))
        if len(idx):
            j, i = idx[0]
            print('first eta NaN at j,i=', j, i, 'x=%.0f y=%.0f depth=%.3f mask=%s' % (xs[i], ys[j], depth[j, i], mask[j, i]))
        idxu = np.argwhere(~np.isfinite(u))
        if len(idxu):
            j, i = idxu[0]
            print('first u NaN at j,i=', j, i, 'x=%.0f y=%.0f' % (xs[min(i, len(xs)-1)], ys[min(j, len(ys)-1)]), 'uf_wet', solver.uf_wet[j, i])
        # print neighbors of eta
        if len(idx):
            j, i = idx[0]
            sl = (slice(max(0,j-3), min(eta.shape[0], j+4)), slice(max(0,i-3), min(eta.shape[1], i+4)))
            print('eta window:', np.array2string(eta[sl], precision=4, max_line_width=200))
            print('depth window:', np.array2string(depth[sl], precision=3, max_line_width=200))
        break
    if k % 2000 == 0:
        print('t=%.1f h eta %.2e u %.3f' % (k*2/3600, np.abs(eta).max(), np.abs(u).max()))
