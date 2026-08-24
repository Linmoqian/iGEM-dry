# -*- coding: utf-8 -*-
"""Exchange (open-boundary source/sink) sensitivity + speed-dependent Cd (Wu 1980) test.
Both use 12 h spin-up from rest on the new domain."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI, wind_stress
from swflow.viz import cell_velocities
PROC = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
dom = np.load(os.path.join(PROC, "domain.npz"))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])

def run(cfg, tau, hours=12.0, sources=None):
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    if sources:
        for (j, i, q) in sources:
            solver.add_source(j, i, q)
    for _ in range(int(hours*3600.0/cfg.dt)):
        solver.step(st, tau[0], tau[1])
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2+vc**2)
    return st, sp

# find candidate gate cells: 东湖港/青山港 area = NE channel of lake; 新沟/九峰港 = SW outlet.
# use extremes of the water mask: NE-most wet cell, SW-most wet cell
jj, ii = np.where(mask)
ne = (jj + ii).argmax()    # NE-most
sw = (jj + ii).argmin()
print("NE gate cell (j,i):", jj[ne], ii[ne], "x=%.0f y=%.0f" % (xs[ii[ne]], ys[jj[ne]]))
print("SW gate cell (j,i):", jj[sw], ii[sw], "x=%.0f y=%.0f" % (xs[ii[sw]], ys[jj[sw]]))

cfg_base = SweConfigSI(dx=dx, dt=20.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode="smag")
tau, ty, cd = wind_stress(2.5, 135.0)

# A: closed basin (reference)
st0, sp0 = run(cfg_base, (tau, ty))
print("closed: |u|max=%.4f mean=%.4f" % (float(sp0[mask].max()), float(sp0[mask].mean())))

# B: exchange = +5 m3/s at NE gate, -5 m3/s at SW gate (引江济湖雏形; Q magnitude = 武丰闸泵站量级的保守下限)
cfgx = cfg_base
st1, sp1 = run(cfgx, (tau, ty), sources=[(jj[ne], ii[ne], +5.0), (jj[sw], ii[sw], -5.0)])
print("exchange +-5 m3/s: |u|max=%.4f mean=%.4f" % (float(sp1[mask].max()), float(sp1[mask].mean())))
print("exchange local speed at NE gate: %.4f m/s" % float(np.sqrt(st1["u"][jj[ne], ii[ne]+1]**2 + st1["v"][jj[ne]+1, ii[ne]]**2)))

# C: Cd(Wu 1980) speed-dependent
ta_wu, ty_wu, cd_wu = wind_stress(2.5, 135.0, cd_mode="wu")
print("Cd(wu@2.5)=%.4f vs const Cd=%.4f" % (cd_wu, cd))
st2, sp2 = run(cfg_base, (ta_wu, ty_wu))
print("Cd-wu: |u|max=%.4f mean=%.4f (vs const %.4f)" % (float(sp2[mask].max()), float(sp2[mask].mean()), float(sp0[mask].mean())))

np.savez_compressed(os.path.join(PROC, "flow_exchange5.npz"), u=st1["u"], v=st1["v"], eta=st1["eta"],
                    uc=cell_velocities(st1)[0], vc=cell_velocities(st1)[1], mask=mask, depth=depth,
                    xs=xs, ys=ys, dx=dx, wind_mps=2.5, wind_dir=135.0, label="exch5")
print("saved flow_exchange5.npz")
