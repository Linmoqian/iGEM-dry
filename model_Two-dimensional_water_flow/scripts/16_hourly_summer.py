# -*- coding: utf-8 -*-
"""E2: diurnal lake-breeze signal in the project's own Open-Meteo data (hu Hui et al. 2018
claims: lake wind starts 07-08h, max 1-2.2 m/s, summer duration 13h), and how a
time-varying summer wind field changes circulation & a drop's coverage vs steady SE 2.5.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI, wind_stress
from swflow.viz import cell_velocities
import swflow.particles as particles
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from swflow.viz import setup_style
setup_style()

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")

d = json.load(open(os.path.join(ROOT, "data", "raw", "openmeteo_wind_enghu_2023_2024.json"), encoding="utf-8"))
h = d["hourly"]
t = h["time"]
spd_kmh = np.array(h["wind_speed_10m"], float)
dirn = np.array(h["wind_direction_10m"], float)
spd = spd_kmh/3.6
print("station: %.4fN %.4fE; n=%d; %s .. %s" % (d["latitude"], d["longitude"], len(t), t[0], t[-1]))

# ---- JJA diurnal climatology ----
months = [tt[5:7] for tt in t]
jj = [i for i, tt in enumerate(t) if tt[5:7] in ("06", "07", "08")]
hrs = np.array([int(tt[11:13]) for tt in t])
print("\n=== JJA diurnal wind (project data, %.4fN) ===" % d["latitude"])
day_h = np.arange(0, 24)
dm = [spd[jj][hrs[jj] == k].mean() if (hrs[jj] == k).any() else np.nan for k in day_h]
print("hour:   " + " ".join("%2d" % k for k in range(24)))
print("speed:  " + " ".join("%4.2f" % v for v in dm))
# circular mean direction per hour (JJA)
cxy = []
for k in range(24):
    ang = np.radians(dirn[jj][hrs[jj] == k])
    if len(ang) > 0:
        c = np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())
        cxy.append(round((np.degrees(c) % 360.0), 0))
    else:
        cxy.append(np.nan)
print("dir(circ): " + " ".join("%4.0f" % v for v in cxy))
mask_d = np.array([np.isfinite(v) for v in dm])
print("day 08-19 mean speed: %.2f m/s ; night 20-07 mean: %.2f m/s" %
      (np.nanmean(dm[8:20]), np.nanmean([dm[k] for k in list(range(20,24))+list(range(0,8))])))
print("day 08-19 circ mean dir: %.0f deg ; night circ mean dir: %.0f deg" %
      (np.degrees(np.arctan2(np.mean([np.sin(np.radians(v)) for v in cxy[8:20]]),
                             np.mean([np.cos(np.radians(v)) for v in cxy[8:20]]))) % 360,
       np.degrees(np.arctan2(np.mean([np.sin(np.radians(v)) for v in [cxy[k] for k in list(range(20,24))+list(range(0,8))]]),
                             np.mean([np.cos(np.radians(v)) for v in [cxy[k] for k in list(range(20,24))+list(range(0,8))]]))) % 360))

# ---- July 2023: 72 h time-varying run ----
i0 = t.index("2023-07-15T00:00")
wspd = spd[i0:i0+72]; wdir = dirn[i0:i0+72]; tsl = t[i0:i0+72]
print("\n72h window: mean %.2f m/s max %.2f ; dir range [%.0f, %.0f]" %
      (wspd.mean(), wspd.max(), wdir.min(), wdir.max()))
dom = dict(np.load(os.path.join(PROC, "domain.npz")))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])
cfg = SweConfigSI(dx=dx, dt=40.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode="smag")
solver = ShallowWaterSolverSI(mask, depth, cfg)
st = solver.init_state()
fields = []
for k in range(72):
    tau_x, tau_y, _ = wind_stress(float(wspd[k]), float(wdir[k]), cd=cfg.c_d_wind)
    for _ in range(int(3600.0/cfg.dt)):
        solver.step(st, tau_x, tau_y)
    uc, vc = cell_velocities(st)
    fields.append((k, uc, vc))
    if k % 24 == 0:
        sp = np.sqrt(uc**2+vc**2)
        print("  hour %d: wind %.2f m/s %d deg -> |u|max %.4f mean %.4f" % (k, wspd[k], wdir[k], sp[mask].max(), sp[mask].mean()))

np.savez_compressed(os.path.join(PROC, "flow_2023jul_hourly72.npz"),
                    uc=[f[1] for f in fields], vc=[f[2] for f in fields],
                    mask=mask, depth=depth, xs=xs, ys=ys, dx=dx,
                    wspd=wspd, wdir=wdir, times=tsl)

# ---- control: steady SE 2.5, 24 h ----
cfg2 = SweConfigSI(dx=dx, dt=40.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode="smag")
sol2 = ShallowWaterSolverSI(mask, depth, cfg2)
st2 = sol2.init_state()
tau_x, tau_y, _ = wind_stress(2.5, 135.0, cd=cfg2.c_d_wind)
for _ in range(int(24*3600.0/cfg2.dt)):
    sol2.step(st2, tau_x, tau_y)
uc2, vc2 = cell_velocities(st2)
np.savez_compressed(os.path.join(PROC, "flow_SE_2p5_control24.npz"), u=st2["u"], v=st2["v"], eta=st2["eta"],
                    uc=uc2, vc=vc2, mask=mask, depth=depth, xs=xs, ys=ys, dx=dx, wind_mps=2.5, wind_dir=135.0)
print("control steady SE2.5 24h: |u|max %.4f mean %.4f" % (np.sqrt(uc2**2+vc2**2)[mask].max(), np.sqrt(uc2**2+vc2**2)[mask].mean()))

# ---- time-varying tracer wrapper ----
class TimeVaryingTracer(particles.ParticleTracer):
    def __init__(self, fields, mask, xs, ys, dx, rng=None, hour_dt=3600.0):
        super().__init__(fields[0][1], fields[0][2], mask, xs, ys, dx, rng)
        self.fields = fields
        self.hour_dt = hour_dt
    def _flow_at(self, x, y, hour):
        f = min(int(hour), len(self.fields)-1)
        self.uc = self.fields[f][1]; self.vc = self.fields[f][2]
        return self._flow(x, y)
    def advect_tv(self, pos, t_hour, D=0.0, dt=5.0):
        x, y = pos[:, 0].copy(), pos[:, 1].copy()
        k1x, k1y = self._flow_at(x, y, t_hour)
        k2x, k2y = self._flow_at(x + 0.5*dt*k1x, y + 0.5*dt*k1y, t_hour)
        k3x, k3y = self._flow_at(x + 0.5*dt*k2x, y + 0.5*dt*k2y, t_hour)
        k4x, k4y = self._flow_at(x + dt*k3x, y + dt*k3y, t_hour)
        xn = x + dt*(k1x + 2*k2x + 2*k3x + k4x)/6.0
        yn = y + dt*(k1y + 2*k2y + 2*k3y + k4y)/6.0
        if D > 0:
            s = np.sqrt(2*D*dt)
            xn = xn + s*self.rng.standard_normal(x.shape)
            yn = yn + s*self.rng.standard_normal(x.shape)
        x0, y0 = x.copy(), y.copy()
        ok = self.in_water(xn, yn)
        niter = 0
        while (~ok).any() and niter < 10:
            bad = ~ok
            xn[bad] = x0[bad] + 0.5*(xn[bad]-x0[bad]); yn[bad] = y0[bad] + 0.5*(yn[bad]-y0[bad])
            ok = self.in_water(xn, yn); niter += 1
        b = ~self.in_water(xn, yn)
        if b.any():
            xn[b] = x0[b]; yn[b] = y0[b]
        return np.column_stack([xn, yn])

def drop_tv(tr, pos0, t0_hour, T_s, dt=5.0, D=0.3):
    pos = pos0.copy()
    nn = int(round(T_s/dt))
    for k in range(nn):
        pos = tr.advect_tv(pos, t0_hour + k*dt/3600.0, D=D, dt=dt)
    return pos

drop_xy = (-1300.0, -200.0)
n, sigma0 = 2500, 25.0
T_h = 2.0
res_summary = {}
# release at 07:00 local on 2023-07-16 (= hour 31 of the window; 00:00 = hour 0 of 07-15)
for rel_h in [1, 31, 55]:
    rng = np.random.default_rng(11)
    pos0 = rng.standard_normal((n, 2))*sigma0 + np.array(drop_xy)
    tr = TimeVaryingTracer(fields, mask, xs, ys, dx, rng=np.random.default_rng(17))
    pend = drop_tv(tr, pos0, rel_h, T_h*3600.0)
    C = tr.density(pend, sigma_m=30.0)
    C0 = tr.density(pos0, sigma_m=30.0)
    thr = 0.05*C0.max()
    cov = (C >= thr) & mask
    A = cov.sum()*dx*dx/1e6
    res_summary[rel_h] = (A, pend.mean(axis=0))
    print("TV drop rel at hour %d (%s 07:00=True? ): area=%.4f km2 centroid=(%.0f,%.0f)"
          % (rel_h, tsl[rel_h], A, pend.mean(axis=0)[0], pend.mean(axis=0)[1]))
# steady control drop (SE 2.5)
rng = np.random.default_rng(11)
pos0 = rng.standard_normal((n, 2))*sigma0 + np.array(drop_xy)
tr0 = particles.ParticleTracer(uc2, vc2, mask, xs, ys, dx, rng=np.random.default_rng(17))
pend, _ = tr0.run(pos0, T_h*3600.0, dt=5.0, D=0.3)
C = tr0.density(pend, sigma_m=30.0); C0 = tr0.density(pos0, sigma_m=30.0)
cov = (C >= 0.05*C0.max()) & mask
print("steady SE2.5 drop: area=%.4f km2 centroid=(%.0f,%.0f)" % (cov.sum()*dx*dx/1e6, pend.mean(0)[0], pend.mean(0)[1]))
json.dump({str(k): [res_summary[k][0], list(res_summary[k][1])] for k in res_summary},
          open(os.path.join(ROOT, "data", "processed", "e2_summary.json"), "w"), indent=1)

# figure: diurnal cycle + wind & flow time series
fig, axes = plt.subplots(2, 2, figsize=(14, 7.5))
axes[0][0].bar(day_h, dm, color="tab:blue")
axes[0][0].set_xticks(range(0, 24, 2)); axes[0][0].set_title("JJA diurnal mean wind speed (m/s)")
axes[0][1].bar(day_h, cxy, color="tab:orange")
axes[0][1].set_xticks(range(0, 24, 2)); axes[0][1].set_title("JJA diurnal circ-mean direction (deg)")
axes[1][0].plot(wspd, label="wind (m/s)")
spmax = [np.sqrt(f[1][mask]**2+f[2][mask]**2).max() for f in fields]
axes[1][0].plot(spmax, label="flow |u|max"); axes[1][0].legend(fontsize=8)
axes[1][0].set_title("72h wind & flow max")
axes[1][1].plot(wdir, label="wind dir (deg)"); axes[1][1].legend(fontsize=8)
axes[1][1].set_title("72h wind direction")
plt.tight_layout(); fig.savefig(os.path.join(FIG, "fig10_hourly_wind_summer.png"), dpi=130)
print("saved fig10")
