# -*- coding: utf-8 -*-
"""Bisect the destabilizing term."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
from swflow.swe import ShallowWaterSolver, SweConfig, wind_stress
PROC = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
dom = np.load(os.path.join(PROC, 'domain.npz'))
mask, depth, xs, ys, dx = dom['mask'], dom['depth'], dom['xs'], dom['ys'], float(dom['dx'])
np.seterr(all='ignore')

def trial(name, adv, cor, nu, dt=2.0, steps=3600):
    cfg = SweConfig(dx=dx, dt=dt, n_manning=0.022, nu=nu, use_adv=adv, use_coriolis=cor)
    solver = ShallowWaterSolver(mask, depth, cfg)
    st = solver.init_state()
    tau_x, tau_y = wind_stress(2.5, 135.0)
    ok = True
    for k in range(steps):
        solver.step(st, tau_x, tau_y)
        if not (np.isfinite(st['eta']).all() and np.isfinite(st['u']).all()):
            ok = False
            break
    print('%s: ok=%s steps=%d eta_max=%.3e u_max=%.3e' % (name, ok, k if not ok else steps,
          np.abs(st['eta']).max(), np.abs(st['u']).max()))
    return ok

trial('no-adv no-cor nu=0.5', False, False, 0.5)
trial('adv off cor on nu=0.5', False, True, 0.5)
trial('adv on cor off nu=0.5', True, False, 0.5)
trial('adv on cor on nu=0.5 (full)', True, True, 0.5)
