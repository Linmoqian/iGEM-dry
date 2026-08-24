# -*- coding: utf-8 -*-
"""Replicate the MIKE21 Donghu simulation period: 2017-11-15 00:00 -> 2017-12-17 00:00.
Time-varying wind from Open-Meteo history at the lake center; dt=40 s; hourly flow snapshots."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI, wind_stress
from swflow.viz import cell_velocities

PROC = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
dom = np.load(os.path.join(PROC, "domain.npz"))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])

# fetch 2017-11-01 .. 2017-12-20 wind from Open-Meteo archive
import urllib.request
url = ("https://archive-api.open-meteo.com/v1/archive?latitude=30.557&longitude=114.404"
       "&start_date=2017-11-01&end_date=2017-12-20&hourly=wind_speed_10m,wind_direction_10m"
       "&timezone=Asia%2FShanghai")
d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "iGEM/1.0"}), timeout=120).read().decode())
spd = np.array(d["hourly"]["wind_speed_10m"], float)/3.6
dirn = np.array(d["hourly"]["wind_direction_10m"], float)
times = d["hourly"]["time"]
print("n hours:", len(spd), "range:", times[0], times[-1])
# select window
t0 = "2017-11-15T00:00"; t1 = "2017-12-17T00:00"
i0 = times.index(t0); i1 = times.index(t1)
spd_w = spd[i0:i1]; dirn_w = dirn[i0:i1]; times_w = times[i0:i1]
print("window hours:", len(spd_w), "mean spd %.2f" % spd_w.mean())

cfg = SweConfigSI(dx=dx, dt=40.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode="smag")
solver = ShallowWaterSolverSI(mask, depth, cfg)
st = solver.init_state()
snaps = {"t": [], "spd": [], "dir": [], "umax": [], "umean": [], "uc": [], "vc": [], "eta": []}
for h, (s_, dd) in enumerate(zip(spd_w, dirn_w)):
    tau, ty, _ = wind_stress(float(s_), float(dd), cd=cfg.c_d_wind)
    for _ in range(int(3600.0/cfg.dt)):
        solver.step(st, tau, ty)
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2+vc**2)
    snaps["t"].append(times_w[h]); snaps["spd"].append(float(s_)); snaps["dir"].append(float(dd))
    snaps["umax"].append(float(sp[mask].max())); snaps["umean"].append(float(sp[mask].mean()))
    if h % 6 == 0:
        snaps["uc"].append(uc.copy()); snaps["vc"].append(vc.copy()); snaps["eta"].append(st["eta"].copy())
print("done; mean |u|max=%.3f mean |u|mean=%.4f" % (np.mean(snaps["umax"]), np.mean(snaps["umean"])))
np.savez_compressed(os.path.join(PROC, "flow_2017period_hourly.npz"), **{k: (np.array(v) if k != "uc" else v) for k, v in snaps.items()})
