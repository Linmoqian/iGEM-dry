# -*- coding: utf-8 -*-
"""(A) rectangular basin stability; (B) real domain without friction"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
from swflow.swe import ShallowWaterSolver, SweConfig, wind_stress
PROC = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
np.seterr(all='ignore')

def run(name, mask, depth, n_manning, nu, steps=6000, adv=False, cor=False, dt=2.0):
    cfg = SweConfig(dx=50.0, dt=dt, n_manning=n_manning, nu=nu, use_adv=adv, use_coriolis=cor)
    solver = ShallowWaterSolver(mask, depth, cfg)
    st = solver.init_state()
    tau_x, tau_y = wind_stress(2.5, 135.0)
    ok = True
    for k in range(steps):
        solver.step(st, tau_x, tau_y)
        if not np.isfinite(st['eta']).all():
            ok = False; break
    print('%s: ok=%s steps=%d eta_max=%.3e u_max=%.3e' % (name, ok, k if not ok else steps,
          np.abs(st['eta']).max(), np.abs(st['u']).max()))
    return ok

# A: rectangular basin 50 x 50 cells, uniform depth 2.3
mask_rect = np.ones((50, 50), bool)
depth_rect = np.full((50, 50), 2.3)
run('rect n=0.022 nu=0.5', mask_rect, depth_rect, 0.022, 0.5)
run('rect n=0.000 nu=0.5', mask_rect, depth_rect, 0.000, 0.5)
run('rect n=0.000 nu=0.0', mask_rect, depth_rect, 0.000, 0.0)

# B: real domain no friction
dom = np.load(os.path.join(PROC, 'domain.npz'))
mask, depth = dom['mask'], dom['depth']
run('donghu n=0.0 nu=0.5', mask, depth, 0.0, 0.5, steps=3000)
run('donghu n=0.0 nu=1.0', mask, depth, 0.0, 1.0, steps=3000)
