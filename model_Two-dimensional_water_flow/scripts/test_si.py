# -*- coding: utf-8 -*-
"""Validate semi-implicit solver: wave test + wind rect test"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI
from swflow.swe import wind_stress
np.seterr(all="ignore")

nx, ny = 240, 24
dx = 50.0
mask = np.ones((ny, nx), bool)
depth = np.full((ny, nx), 4.0)
cfg = SweConfigSI(dx=dx, dt=5.0, n_manning=0.0, nu=0.0, use_adv=False, use_coriolis=False, h_dry=0.0)
solver = ShallowWaterSolverSI(mask, depth, cfg)
st = solver.init_state()
L = nx*dx; c = np.sqrt(9.81*4.0)
x = (np.arange(nx)+0.5)*dx
st["eta"][:, :] = (0.02*np.cos(np.pi*x/L))[None, :]
T_an = 2*L/c
vol0 = solver.volume(st)
ts = [0.0]; es = [float(st["eta"][:, nx//2].mean())]
for k in range(int(2.2*T_an/cfg.dt)):
    solver.step(st, 0.0, 0.0)
    if k % 40 == 0:
        ts.append((k+1)*cfg.dt); es.append(float(st["eta"][:, nx//2].mean()))
es = np.array(es); ts = np.array(ts)
zc = []
for i in range(1, len(es)):
    if es[i-1] > 0 and es[i] <= 0:
        t0, t1 = ts[i-1], ts[i]
        zc.append(t0 + (t1-t0)*(es[i-1])/(es[i-1]-es[i]))
if len(zc) >= 2:
    T_num = 2*np.mean(np.diff(zc[:min(4, len(zc)-1)]))
    print("SI wave: T=%.1f vs %.1f  err=%.2f%%" % (T_num, T_an, 100*abs(T_num-T_an)/T_an))
print("SI wave: volume drift %.2e, peak |eta| %.4f" % (abs(solver.volume(st)-vol0)/vol0, np.abs(st["eta"]).max()))

mask2 = np.ones((50, 50), bool)
depth2 = np.full((50, 50), 2.3)
cfg2 = SweConfigSI(dx=50.0, dt=20.0, n_manning=0.022, nu=0.5, use_adv=False, use_coriolis=False)
solver2 = ShallowWaterSolverSI(mask2, depth2, cfg2)
st2 = solver2.init_state()
tau_x, tau_y = wind_stress(2.5, 135.0)
vol0 = solver2.volume(st2)
for k in range(24*3600//20):
    solver2.step(st2, tau_x, tau_y)
    if k % 720 == 0:
        print("t=%dh eta_max=%.4f u_max=%.4f u_mean=%.5f" % (k*20/3600, np.abs(st2["eta"]).max(), np.abs(st2["u"]).max(), st2["u"].mean()))
print("rect wind: vol drift %.2e" % (abs(solver2.volume(st2)-vol0)/vol0))
row = 25
print("eta profile row 25:", st2["eta"][row, 0], st2["eta"][row, 25], st2["eta"][row, 49])
