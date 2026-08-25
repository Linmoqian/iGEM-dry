# -*- coding: utf-8 -*-
"""E6: rebuild the wind-scenario library and the corrected wind climatology from the
project's own Open-Meteo data (2023-2024, hourly). Replaces the undocumented
"静风21.8% / 年均1.8-2.3 m/s" figures (P1-2) with in-house statistics, and checks
the existing SE2.5 / N3.0 / W2.0 scenarios against sector- and seasonal quantiles.
Cross-check against Donghu monthly wind regime from Tian Yong (2012, cited in
Guo Xuerui 2018 thesis Table 4-1): annual mean 2.8 m/s, Jan-Mar & Oct-Dec from 20-30 deg,
Apr-May 110-120 deg, Jun-Aug 130-180 deg.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

ROOT = os.path.join(os.path.dirname(__file__), "..")
d = json.load(open(os.path.join(ROOT, "data", "raw", "openmeteo_wind_enghu_2023_2024.json"), encoding="utf-8"))
h = d["hourly"]
t = h["time"]; spd = np.array(h["wind_speed_10m"], float)/3.6; dirn = np.array(h["wind_direction_10m"], float)
print("station %.4fN %.4fE, %d hours, mean=%.2f m/s, median=%.2f" %
      (d["latitude"], d["longitude"], len(spd), spd.mean(), np.median(spd)))
print("calm <0.5 m/s: %.1f%%   <1 m/s: %.1f%%   >=5 m/s: %.1f%%" %
      (100*(spd<0.5).mean(), 100*(spd<1.0).mean(), 100*(spd>=5).mean()))

SECTORS = ["N","NE","E","SE","S","SW","W","NW"]
def sector(dg): return int(np.floor(((dg+22.5) % 360.0)/45.0))
tmp = np.array([sector(x) for x in dirn])
print("\nannual sector stats:")
for k in range(8):
    m = tmp == k
    if m.sum() == 0: continue
    print("  %-3s freq=%5.1f%%  mean=%4.2f  p50=%4.2f  p75=%4.2f  p90=%4.2f  circ_mean=%4.0f deg"
          % (SECTORS[k], 100*m.mean(), spd[m].mean(), np.percentile(spd[m], 50),
             np.percentile(spd[m], 75), np.percentile(spd[m], 90),
             (np.degrees(np.arctan2(np.sin(np.radians(dirn[m])).mean(), np.cos(np.radians(dirn[m])).mean())) % 360)))

circ = np.radians(dirn)
circ_annual = np.degrees(np.arctan2(np.sin(circ).mean(), np.cos(circ).mean())) % 360
print("annual circular-mean direction: %.0f deg" % circ_annual)

seasons = {"DJF": ("12","01","02"), "MAM": ("03","04","05"), "JJA": ("06","07","08"), "SON": ("09","10","11")}
print("\nseasonal stats:")
for sn, mm in seasons.items():
    m = np.array([tt[5:7] in mm for tt in t])
    ang = np.radians(dirn[m])
    cdir = np.degrees(np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())) % 360
    print("  %s: mean=%4.2f  p50=%4.2f  p90=%4.2f  circ-mean=%4.0f  calm<0.5: %.1f%%"
          % (sn, spd[m].mean(), np.percentile(spd[m], 50), np.percentile(spd[m], 90), cdir, 100*(spd[m]<0.5).mean()))

print("\nexisting scenarios vs sector quantiles:")
for lab, spd_v, dir_v in [("SE_2p5", 2.5, 135.0), ("N_3p0", 3.0, 0.0), ("W_2p0", 2.0, 270.0)]:
    k = sector(dir_v); m = tmp == k
    print("  %s (%.1f m/s from %.0f deg): sector %s freq %.1f%%  -> within-sector percentile %.0f%% (p50 %.2f, p90 %.2f)"
          % (lab, spd_v, dir_v, SECTORS[k], 100*m.mean(), 100*((spd[m] < spd_v).mean()),
             np.percentile(spd[m], 50), np.percentile(spd[m], 90)))

print("\nproposed quantile scenario library (sector, p50/p75/p90):")
for k in range(8):
    m = tmp == k
    if m.sum() == 0: continue
    print("  %-3s  p50=%4.2f  p75=%4.2f  p90=%4.2f  (n=%d)" % (SECTORS[k], np.percentile(spd[m], 50),
          np.percentile(spd[m], 75), np.percentile(spd[m], 90), m.sum()))
