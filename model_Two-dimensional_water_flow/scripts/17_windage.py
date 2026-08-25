# -*- coding: utf-8 -*-
"""E3: surface wind-drift (windage) sensitivity for the particle layer.
2D depth-averaged currents underestimate the surface layer speed in wind-driven flow
(Fenocchi et al. 2016; Wang et al. 2017 for Microcystis surface banding). Standard
lagrangian practice adds a windage term: dx = (u + w_a * W_10) * dt with a fraction
of the 10-m wind; direction = wind direction (Ekman rotation ignored for a first cut).
Compare coverage / centroid / area for w_a in {0, 1%, 2%, 3%, 5%} under SE 2.5.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.particles import ParticleTracer
from swflow.deployment import release_positions

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
f = dict(np.load(os.path.join(PROC, "flow_SE_2p5.npz")))
uc, vc, mask, xs, ys, dx = f["uc"], f["vc"], f["mask"], f["xs"], f["ys"], float(f["dx"])
W = 2.5    # m/s
th = np.radians(135.0)
wvec = np.array([-np.sin(th), -np.cos(th)]) * W   # wind velocity vector (blows toward 315 deg)

class WindageTracer(ParticleTracer):
    def __init__(self, uc, vc, mask, xs, ys, dx, wvec, w_a, rng=None):
        super().__init__(uc, vc, mask, xs, ys, dx, rng)
        self.wvec = wvec; self.w_a = w_a
    def advect(self, pos, D=0.0, dt=1.0):
        t_add = self.w_a * self.wvec
        p2 = pos.copy(); p2[:, 0] += t_add[0]*dt/2.0; p2[:, 1] += t_add[1]*dt/2.0
        out = super().advect(p2, D=D, dt=dt)
        out[:, 0] += t_add[0]*dt/2.0; out[:, 1] += t_add[1]*dt/2.0
        return out

drop_xy = (-1300.0, -200.0)
for w_a in [0.00, 0.01, 0.02, 0.03, 0.05]:
    tr = WindageTracer(uc, vc, mask, xs, ys, dx, wvec, w_a, rng=np.random.default_rng(7))
    pos0 = release_positions(drop_xy, 2500, 25.0, tr.rng)
    pend, _ = tr.run(pos0, 2.0*3600.0, dt=5.0, D=0.3)
    C = tr.density(pend, sigma_m=30.0)
    C0 = tr.density(pos0, sigma_m=30.0)
    thr = 0.05*C0.max()
    cov = (C >= thr) & mask
    drift = pend.mean(axis=0) - pos0.mean(axis=0)
    print("windage %.0f%%: area=%.4f km2  drift=(%+4.0f, %+4.0f) m  peak=%.2e"
          % (100*w_a, cov.sum()*dx*dx/1e6, drift[0], drift[1], C.max()))
