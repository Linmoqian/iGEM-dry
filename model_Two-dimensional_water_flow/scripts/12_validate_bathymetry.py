# -*- coding: utf-8 -*-
"""E0: validate the reconstructed bathymetry against 42 in-situ depth soundings.
Data source: 刘惠 et al. (2019, 华中师范大学学报(自然科学版) 53(5):765-772,
doi:10.19603/j.cnki.1000-1190.2019.05.015, "长江经济带湖泊水下地形的热红外遥感反演——以武汉市东湖为例")
Table 1 gives 42 measured water depths (2017-07-23, water level 19.18 m Wusong) with coordinates;
Table 2 lists the same depths corrected to the image day (+0.12 m, level 19.30 m);
we verify Table1+0.12 == Table2 internally, then compare with the model depth field.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import swflow.domain as dom

# (point, lon, lat, depth_20170723) — digitized from Liu et al. 2019 Table 1
# (each entry cross-checked: Table1 depth + 0.12 == Table2 H, 42/42)
POINTS = [
 (1, 114.374561, 30.578364, 2.30), (2, 114.375550, 30.577950, 2.30),
 (3, 114.376339, 30.577242, 2.34), (4, 114.377981, 30.574828, 2.65),
 (5, 114.378656, 30.572661, 3.16), (6, 114.379042, 30.570489, 3.10),
 (7, 114.379989, 30.569006, 3.20), (8, 114.381050, 30.566097, 3.32),
 (9, 114.382183, 30.563269, 3.40), (10, 114.384672, 30.557397, 3.42),
 (11, 114.387319, 30.552503, 3.55), (12, 114.388661, 30.550000, 3.55),
 (13, 114.386922, 30.549781, 3.60), (14, 114.380853, 30.549542, 3.65),
 (15, 114.374292, 30.549453, 3.60), (16, 114.366292, 30.549561, 2.78),
 (17, 114.363467, 30.549842, 2.95), (18, 114.355711, 30.549781, 2.30),
 (19, 114.357044, 30.549572, 2.70), (20, 114.360603, 30.549464, 2.80),
 (21, 114.364436, 30.549511, 3.60), (22, 114.368547, 30.549472, 3.40),
 (23, 114.371569, 30.549647, 3.60), (24, 114.373903, 30.549858, 3.60),
 (25, 114.376458, 30.550106, 3.62), (26, 114.381100, 30.551006, 3.65),
 (27, 114.385481, 30.551631, 3.72), (28, 114.389633, 30.552589, 3.52),
 (29, 114.394047, 30.553597, 2.92), (30, 114.395789, 30.554142, 2.42),
 (31, 114.398092, 30.554736, 2.32), (32, 114.403964, 30.557186, 1.98),
 (33, 114.407425, 30.557597, 2.44), (34, 114.411172, 30.556842, 2.60),
 (35, 114.413997, 30.556258, 2.60), (36, 114.383422, 30.555994, 2.93),
 (37, 114.419533, 30.555625, 3.16), (38, 114.423064, 30.554781, 3.24),
 (39, 114.422819, 30.556869, 3.58), (40, 114.422736, 30.560025, 3.67),
 (41, 114.427894, 30.559172, 2.67), (42, 114.428419, 30.555297, 3.17),
]
H2_CHECK = [2.42,2.42,2.46,2.77,3.28,3.22,3.32,3.44,3.52,3.54,3.67,3.67,3.72,3.77,
            3.72,2.90,3.07,2.42,2.82,2.92,3.72,3.52,3.72,3.72,3.74,3.77,3.84,3.64,
            3.04,2.54,2.44,2.10,2.56,2.72,2.72,3.05,3.28,3.36,3.70,3.79,2.79,3.29]

print("=== internal check: Table1 depth + 0.12 == Table2 H ===")
bad = [i+1 for i, p in enumerate(POINTS) if abs(p[3] + 0.12 - H2_CHECK[i]) > 1e-9]
print("mismatches:", bad if bad else "NONE (42/42 OK)")

dom_npz = dict(np.load(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "domain.npz")))
mask, depth, xs, ys, dx = dom_npz["mask"], dom_npz["depth"], dom_npz["xs"], dom_npz["ys"], float(dom_npz["dx"])
meta = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "domain_meta.json"), encoding="utf-8"))
print("model domain: area=%.2f km2, L=%.1f, mean_target=%.2f max_target=%.2f" %
      (meta["area_km2"], meta["depth_L"], meta["mean_depth_target"], meta["max_depth"]))

def to_grid(lon, lat):
    x, y = dom.project(lon, lat)
    i = int(np.floor((x - xs[0]) / dx)); j = int(np.floor((y - ys[0]) / dx))
    if 0 <= i < len(xs) and 0 <= j < len(ys):
        return j, i, x, y
    return None

obs_d, mod_d, pts_used = [], [], []
for (n, lon, lat, d) in POINTS:
    g = to_grid(lon, lat)
    if g is None:
        print("point", n, "outside grid"); continue
    j, i, x, y = g
    if mask[j, i]:
        obs_d.append(d); mod_d.append(depth[j, i]); pts_used.append(n)
    else:
        print("point", n, "on land cell (mask False) — skip")
obs = np.array(obs_d); mod = np.array(mod_d)
err = mod - obs
print("\n=== measured vs reconstructed (n=%d) ===" % len(pts_used))
print("measured: mean=%.2f  min=%.2f  max=%.2f" % (obs.mean(), obs.min(), obs.max()))
print("model   : mean=%.2f  min=%.2f  max=%.2f" % (mod.mean(), mod.min(), mod.max()))
print("bias (model-measured) = %+.3f m" % err.mean())
print("RMSE = %.3f m" % np.sqrt((err**2).mean()))
print("MAE  = %.3f m" % np.abs(err).mean())
print("R    = %.3f" % np.corrcoef(obs, mod)[0, 1])
print("rel. err (|err|/obs) mean = %.1f%%" % (100*np.abs(err/obs).mean()))
# near-shore vs interior split (depth<2.6 = shallow per Liu et al. "小湖汊水深不到2m" is for bays; use median split)
med = np.median(obs)
sh = obs < med
print("shallow subset (obs<%.2f): bias %+.3f RMSE %.3f n=%d" % (med, err[sh].mean(), np.sqrt((err[sh]**2).mean()), sh.sum()))
print("deep subset   (obs>=%.2f): bias %+.3f RMSE %.3f n=%d" % (med, err[~sh].mean(), np.sqrt((err[~sh]**2).mean()), (~sh).sum()))
print("\nper-point (first 12): n, measured, model, err")
for k in range(min(12, len(pts_used))):
    print("  p%-2d  %.2f  %.2f  %+.2f" % (pts_used[k], obs[k], mod[k], err[k]))
# save
np.savez(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "bathy_validation.npz"),
         obs=obs, mod=mod, pts=pts_used)
print("saved bathy_validation.npz")
