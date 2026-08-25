# -*- coding: utf-8 -*-
"""Validation: 1-D standing wave in a closed rectangular basin (no wind, no friction)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
from swflow.swe import ShallowWaterSolver, SweConfig, G

nx, ny = 240, 24
dx = 50.0
mask = np.ones((ny, nx), bool)
depth = np.full((ny, nx), 4.0)
cfg = SweConfig(dx=dx, dt=0.5, n_manning=0.0, nu=0.0, use_adv=False, use_coriolis=False, h_dry=0.0)
solver = ShallowWaterSolver(mask, depth, cfg)
st = solver.init_state()
L = nx*dx
c = np.sqrt(G*4.0)
x = (np.arange(nx)+0.5)*dx
st['eta'][:, :] = (0.02*np.cos(np.pi*x/L))[None, :]
T_an = 2*L/c
print('T_analytical = %.2f s' % T_an)
ts = [0.0]; es = [float(st['eta'][:, nx//2].mean())]
vol0 = solver.volume(st)
dt = cfg.dt
for k in range(int(2.2*T_an/dt)):
    solver.step(st, 0.0, 0.0)
    if k % 50 == 0:
        ts.append((k+1)*dt); es.append(float(st['eta'][:, nx//2].mean()))
es = np.array(es); ts = np.array(ts)
zc = []
for i in range(1, len(es)):
    if es[i-1] > 0 and es[i] <= 0:
        t0, t1 = ts[i-1], ts[i]
        zc.append(t0 + (t1-t0)*(es[i-1])/(es[i-1]-es[i]))
if len(zc) >= 2:
    T_num = 2*np.mean(np.diff(zc[:min(4, len(zc)-1)]))
    print('T_numerical = %.2f s, error = %.2f%%' % (T_num, 100*abs(T_num-T_an)/T_an))
else:
    print('zero crossings:', zc)
print('volume drift: %.3e m3 (rel %.2e)' % (solver.volume(st)-vol0, abs(solver.volume(st)-vol0)/vol0))
print('eta max |A| =', np.abs(st['eta']).max())
