# -*- coding: utf-8 -*-
"""Diagnose wave amplitude decay: record peak |eta| over time, test dt-convergence."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
from swflow.swe import ShallowWaterSolver, SweConfig, G

def run(dt, nx=240, ny=24):
    dx = 50.0
    mask = np.ones((ny, nx), bool)
    depth = np.full((ny, nx), 4.0)
    cfg = SweConfig(dx=dx, dt=dt, n_manning=0.0, nu=0.0, use_adv=False, use_coriolis=False, h_dry=0.0)
    solver = ShallowWaterSolver(mask, depth, cfg)
    st = solver.init_state()
    L = nx*dx
    x = (np.arange(nx)+0.5)*dx
    st['eta'][:, :] = (0.02*np.cos(np.pi*x/L))[None, :]
    T_an = 2*L/np.sqrt(G*4.0)
    nsteps = int(T_an/dt)
    peaks = []
    for k in range(nsteps):
        solver.step(st, 0.0, 0.0)
        if k % (nsteps//10) == 0:
            peaks.append((k*dt/T_an, float(np.abs(st['eta']).max())))
    return peaks, T_an

for dt in [0.5, 2.0]:
    peaks, T = run(dt)
    print('dt=%.1f  T=%.0f s' % (dt, T))
    print('  ' + '  '.join('t/T=%.1f:%.4f' % p for p in peaks))
