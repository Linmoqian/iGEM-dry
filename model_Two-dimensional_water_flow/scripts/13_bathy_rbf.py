# -*- coding: utf-8 -*-
"""E0b: bathymetry upgrade experiments with the 42 measured soundings.
Compare three depth-field candidates against the in-situ points (LOOCV for fitted ones):
  A. current domain: exponential  d = Dmax*(1-exp(-dist/L)),   Dmax=4.75, L calibrated to mean 2.21
  B. free-fit power-exponential: d = Dmax*(1-exp(-(dist/L)^p)) fitted to the 42 points (LSQ)
  C. GLOBathy-style linear:      d = Dmax*(dist / max_dist)   (Hollister & Milstead 2010 exact form)
  D. residual-corrected field:   d = A + RBF(42 residuals + shoreline anchors)
Then run one SE 2.5 m/s circulation + a single drop test on A vs D.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from scipy.ndimage import distance_transform_edt, binary_erosion, gaussian_filter
from scipy.interpolate import RBFInterpolator
from scipy.optimize import least_squares
import swflow.domain as dom
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
from swflow.viz import setup_style
setup_style()

# --- the 42 measured points (same source/check as 12_validate_bathymetry.py) ---
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
domv = dict(np.load(os.path.join(PROC, "domain.npz")))
mask, depth0, xs, ys, dx = domv["mask"], domv["depth"], domv["xs"], domv["ys"], float(domv["dx"])
ny, nx = mask.shape
dist = distance_transform_edt(mask) * dx          # meters to shore (same as domain.py)
Dmax = float(depth0[mask].max())

# grid index + dist for each measured point
P = []
for (n, lon, lat, d) in POINTS:
    x, y = dom.project(lon, lat)
    i = int(np.floor((x - xs[0]) / dx)); j = int(np.floor((y - ys[0]) / dx))
    if 0 <= i < nx and 0 <= j < ny and mask[j, i]:
        P.append((j, i, d, dist[j, i]))
P = np.array(P, float)
obs, dist_k = P[:, 2], P[:, 3]
print("used points:", len(P))
err0 = depth0[P[:, 0].astype(int), P[:, 1].astype(int)] - obs
print("A exponential: RMSE=%.3f bias=%+.3f R=%.3f" % (np.sqrt((err0**2).mean()), err0.mean(), np.corrcoef(obs, depth0[P[:,0].astype(int), P[:,1].astype(int)])[0,1]))

# --- B: power-exponential free fit ---
def model(params, dd):
    Dm, L, p = params
    return Dm * (1 - np.exp(-np.power(np.maximum(dd, 0.0) / L, p)))
res = least_squares(lambda pr: model(pr, dist_k) - obs, x0=[4.75, 380.0, 1.0],
                    bounds=([2.0, 50.0, 0.3], [7.0, 3000.0, 3.0]))
DmB, LB, pB = res.x
dB_full = model(res.x, dist_k)
errB = dB_full - obs
errB_full = model(res.x, dist_k) - obs
print("B power-exp fit: Dmax=%.2f L=%.1f p=%.2f  RMSE=%.3f bias=%+.3f" % (DmB, LB, pB, np.sqrt((errB_full**2).mean()), errB_full.mean()))
dB = np.where(mask, model(res.x, dist), 0.0)
print("   field mean=%.2f max=%.2f" % (dB[mask].mean(), dB[mask].max()))

# --- B2/B3: production candidates with fixed documented Dmax and mean constraint ---
# 刘惠 2019 documented: max 4.66 m, mean 2.48 m (33.2 km2, 1.24e8 m3)
def model2(params, dd):
    L, p = params
    return 4.66 * (1 - np.exp(-np.power(np.maximum(dd, 0.0) / L, p)))
def field_mean(params):
    return model2(params, dist)[mask].mean()
r2 = least_squares(lambda pr: model2(pr, dist_k) - obs, x0=[300.0, 1.0], bounds=([30.0, 0.2], [3000.0, 3.0]))
LB2, pB2 = r2.x
d2 = np.where(mask, model2(r2.x, dist), 0.0)
print("B2 fixed-Dmax fit: L=%.1f p=%.2f  RMSE(42)=%.3f  field mean=%.2f max=%.2f"
      % (LB2, pB2, np.sqrt(((d2[P[:,0].astype(int), P[:,1].astype(int)] - obs)**2).mean()),
         d2[mask].mean(), d2[mask].max()))
LAM = 1e5  # mean constraint weight (residuals ~m, mean ~m)
r3 = least_squares(lambda pr: np.concatenate([model2(pr, dist_k) - obs,
                                              LAM*np.array([field_mean(pr) - 2.48])]),
                   x0=[LB2, pB2], bounds=([30.0, 0.2], [3000.0, 3.0]))
LB3, pB3 = r3.x
d3 = np.where(mask, model2(r3.x, dist), 0.0)
print("B3 fixed-Dmax+mean fit: L=%.1f p=%.2f  RMSE(42)=%.3f  field mean=%.2f max=%.2f"
      % (LB3, pB3, np.sqrt(((d3[P[:,0].astype(int), P[:,1].astype(int)] - obs)**2).mean()),
         d3[mask].mean(), d3[mask].max()))

# --- C: GLOBathy linear ---
dC = np.where(mask, Dmax * dist / dist[mask].max(), 0.0)
errC = dC[P[:, 0].astype(int), P[:, 1].astype(int)] - obs
print("C GLOBathy linear: RMSE=%.3f bias=%+.3f  field mean=%.2f max=%.2f"
      % (np.sqrt((errC**2).mean()), errC.mean(), dC[mask].mean(), dC[mask].max()))

# --- D: RBF residual correction on A ---
shore = mask & ~binary_erosion(mask, iterations=1)
sj, si = np.where(shore)
# subsample shoreline anchors every ~6 cells
step = 6
anchor = [(sj[k], si[k]) for k in range(0, len(sj), step)]
Aj = np.array([a[0] for a in anchor] + [int(v) for v in P[:, 0]])
Ai = np.array([a[1] for a in anchor] + [int(v) for v in P[:, 1]])
Axy = np.column_stack([xs[Ai], ys[Aj]])
Ar = np.concatenate([np.zeros(len(anchor)), obs - depth0[P[:, 0].astype(int), P[:, 1].astype(int)]])
# grid sample points (subsample 1:2) minus anchor locations for speed
gj, gi = np.where(mask)
sel = (gj % 2 == 0) & (gi % 2 == 0)
gxy = np.column_stack([xs[gi[sel]], ys[gj[sel]]])
rbf = RBFInterpolator(Axy, Ar, kernel="thin_plate_spline", smoothing=0.05)
rhat_grid = np.zeros((ny, nx))
rhat_grid[gj[sel], gi[sel]] = rbf(gxy)
rhat_grid = gaussian_filter(rhat_grid, 2.0)
dD = np.where(mask, depth0 + rhat_grid, 0.0)
dD = np.where(mask, np.clip(dD, 0.10, Dmax + 0.9), 0.0)
errD = dD[P[:, 0].astype(int), P[:, 1].astype(int)] - obs
print("D RBF-corrected: RMSE=%.3f bias=%+.3f  field mean=%.2f max=%.2f"
      % (np.sqrt((errD**2).mean()), errD.mean(), dD[mask].mean(), dD[mask].max()))

# --- LOOCV for D (and B) ---
Aanch_j = Aj[:len(anchor)]; Aanch_i = Ai[:len(anchor)]
Xa = np.column_stack([xs[Aanch_i], ys[Aanch_j]])
oof = []
for k in range(len(P)):
    msk = np.ones(len(P), bool); msk[k] = False
    Xtr = np.column_stack([xs[P[msk, 1].astype(int)], ys[P[msk, 0].astype(int)]])
    rtr = obs[msk] - depth0[P[msk, 0].astype(int), P[msk, 1].astype(int)]
    ra = np.zeros(len(anchor))
    rbf_k = RBFInterpolator(np.vstack([Xa, Xtr]), np.concatenate([ra, rtr]), kernel="thin_plate_spline", smoothing=0.05)
    oof.append(rbf_k(np.array([[xs[int(P[k,1])], ys[int(P[k,0])]]]))[0])
oof = np.array(oof)
print("D LOOCV RMSE=%.3f bias=%+.3f" % (np.sqrt(((oof)**2).mean()), oof.mean()))
oofB = []
for k in range(len(P)):
    msk = np.ones(len(P), bool); msk[k] = False
    r = least_squares(lambda pr: model(pr, dist_k[msk]) - obs[msk], x0=[4.75, 380.0, 1.0],
                      bounds=([2.0, 50.0, 0.3], [7.0, 3000.0, 3.0]))
    oofB.append(model(r.x, np.array([dist_k[k]]))[0] - obs[k])
print("B LOOCV RMSE=%.3f bias=%+.3f" % (np.sqrt((np.array(oofB)**2).mean()), np.array(oofB).mean()))

np.savez_compressed(os.path.join(PROC, "domain_rbf.npz"), mask=mask, depth=dD, xs=xs, ys=ys, dx=dx,
                    depth_exp=depth0, rhat=rhat_grid)
meta = json.load(open(os.path.join(PROC, "domain_meta.json"), encoding="utf-8"))
meta.update({"bathy_RBF": True, "depth_RBF_mean": float(dD[mask].mean()), "depth_RBF_max": float(dD[mask].max()),
             "rbf_rmse_42pts": float(np.sqrt((errD**2).mean())), "rbf_loocv_rmse": float(np.sqrt((oof**2).mean())),
             "exp_rmse_42pts": float(np.sqrt((err0**2).mean()))})
json.dump(meta, open(os.path.join(PROC, "domain_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved domain_rbf.npz + meta")

# --- figure ---
fig, axes = plt.subplots(2, 3, figsize=(18, 8.5))
for ax, d, t in zip(axes[0], [depth0, dB, dD],
                    ["A exp (current): mean %.2f max %.2f" % (depth0[mask].mean(), depth0[mask].max()),
                     "B power-exp fit: mean %.2f max %.2f" % (dB[mask].mean(), dB[mask].max()),
                     "D A+RBF(42pts): mean %.2f max %.2f" % (dD[mask].mean(), dD[mask].max())]):
    im = ax.imshow(d, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap="YlGnBu")
    ax.plot([xs[int(p[1])] for p in P], [ys[int(p[0])] for p in P], "r.", ms=3)
    ax.set_title(t, fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.75)
ax = axes[1][0]
ax.plot(obs, depth0[P[:,0].astype(int), P[:,1].astype(int)], "o", ms=4, label="A exp")
ax.plot(obs, dD[P[:,0].astype(int), P[:,1].astype(int)], "s", ms=4, label="D RBF")
ax.plot([1.5, 4.0], [1.5, 4.0], "k--", lw=0.8)
ax.set_xlabel("measured depth (m)"); ax.set_ylabel("model depth (m)")
ax.set_title("measured vs model (42 pts)"); ax.legend(fontsize=8)
ax = axes[1][1]
ob = np.sort(obs); obm = np.sort(depth0[P[:,0].astype(int), P[:,1].astype(int)])
obmD = np.sort(dD[P[:,0].astype(int), P[:,1].astype(int)])
ax.plot(ob, obm, "o-", ms=3, label="A exp"); ax.plot(ob, obmD, "s-", ms=3, label="D RBF")
ax.set_xlabel("measured (sorted)"); ax.set_ylabel("model"); ax.legend(fontsize=8)
ax.set_title("sorted comparison (same x)")
ax = axes[1][2]
ax.hist(rhat_grid[mask], bins=40); ax.set_xlabel("residual correction (m)"); ax.set_title("RBF correction histogram")
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig07_bathy_validation.png"), dpi=130)
print("saved fig07_bathy_validation.png")
