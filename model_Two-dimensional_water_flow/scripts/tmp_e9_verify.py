# -*- coding: utf-8 -*-
"""E9: production 'lake' wind drag (cd_lake via SweConfigSI.cd_mode) vs constant 1.3e-3.

Three wind scenarios (SE_2.5 / N_3.0 / W_2.0), each spun up 24 h with cd_mode='lake'
and cd_mode='constant'; then a sim_drop comparison on the SE field.
Flow fields saved to data/processed/flow_tmp_e9_*.npz (temporary, not overwriting
production flows).
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI, wind_stress, cd_lake
from swflow.viz import cell_velocities
from swflow.deployment import sim_drop

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
dom = dict(np.load(os.path.join(PROC, "domain.npz")))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])
ny, nx = mask.shape
SPIN_H = 24.0

SCEN = [("SE_2.5", 2.5, 135.0), ("N_3.0", 3.0, 0.0), ("W_2.0", 2.0, 270.0)]

print("== domain: %dx%d, dx=%.0f m, wet=%d, depth mean=%.3f max=%.3f m"
      % (ny, nx, dx, int(mask.sum()), float(depth[mask].mean()), float(depth[mask].max())))

def spin(cfg, tau_x, tau_y):
    t0 = time.time()
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    nsteps = int(SPIN_H * 3600.0 / cfg.dt)
    for _ in range(nsteps):
        solver.step(st, tau_x, tau_y)
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2 + vc**2)
    out = dict(uc=uc, vc=vc, u=st["u"], v=st["v"], eta=st["eta"],
               mask=mask, depth=depth, xs=xs, ys=ys, dx=dx)
    return out, float(sp[mask].max()), float(sp[mask].mean()), time.time() - t0

summary = {}
for lab, U, dgr in SCEN:
    print("\n### scenario %s: U=%.1f m/s dir=%.0f deg" % (lab, U, dgr))
    tau_l, tau_y_l, cd_l = wind_stress(U, dgr, cd=1.3e-3, cd_mode="lake")
    tau_c, tau_y_c, cd_c = wind_stress(U, dgr, cd=1.3e-3, cd_mode="constant")
    print("  cd_lake=%.4g   cd_const=%.4g   ratio=%.3f" % (cd_l, cd_c, cd_l / cd_c))
    print("  tau_lake=(%.4g, %.4g)  tau_const=(%.4g, %.4g)"
          % (tau_l, tau_y_l, tau_c, tau_y_c))
    cfg_l = SweConfigSI(dx=dx, dt=20.0, n_manning=0.0238, use_adv=True,
                        use_coriolis=True, nu_mode="smag", cs=0.29, cd_mode="lake")
    cfg_c = SweConfigSI(dx=dx, dt=20.0, n_manning=0.0238, use_adv=True,
                        use_coriolis=True, nu_mode="smag", cs=0.29, cd_mode="constant")
    f_l, um_l, umn_l, t_l = spin(cfg_l, tau_l, tau_y_l)
    f_c, um_c, umn_c, t_c = spin(cfg_c, tau_c, tau_y_c)
    print("  24h spin lake  : |u|max=%.4f  |u|mean=%.4f  (%.0f s)" % (um_l, umn_l, t_l))
    print("  24h spin const : |u|max=%.4f  |u|mean=%.4f  (%.0f s)" % (um_c, umn_c, t_c))
    print("  ratio max=%.3f  mean=%.3f" % (um_l / um_c, umn_l / umn_c))
    # speed ratio field (cell-centered)
    sp_l = np.sqrt(f_l["uc"]**2 + f_l["vc"]**2)
    sp_c = np.sqrt(f_c["uc"]**2 + f_c["vc"]**2)
    r = sp_l / np.maximum(sp_c, 1e-6)
    print("  speed ratio lake/const: wet-mean=%.3f  min=%.2f  max=%.2f  p10=%.2f p90=%.2f"
          % (float(r[mask].mean()), float(r[mask].min()), float(r[mask].max()),
             float(np.percentile(r[mask], 10)), float(np.percentile(r[mask], 90))))
    # eta stats
    print("  eta lake: max=%.4f min=%.4f | eta const: max=%.4f min=%.4f"
          % (float(f_l["eta"][mask].max()), float(f_l["eta"][mask].min()),
             float(f_c["eta"][mask].max()), float(f_c["eta"][mask].min())))
    for mode, f in (("lake", f_l), ("const", f_c)):
        np.savez_compressed(os.path.join(PROC, "flow_tmp_e9_%s_%s.npz" % (lab, mode)),
                            **dict(f, wind_mps=U, wind_dir=dgr))
    summary[lab] = dict(U=U, dgr=dgr, cd_l=cd_l, cd_c=cd_c, um_l=um_l, umn_l=umn_l,
                        um_c=um_c, umn_c=umn_c)

# ---- sim_drop comparison on the SE field (drop at (-1300,-200)) ----
print("\n### sim_drop SE field: drop=(-1300,-200) T_h=2h thr_rel=0.05 n=2500")
DROP = (-1300.0, -200.0)
i0 = int(round((DROP[0] - xs[0]) / dx)); j0 = int(round((DROP[1] - ys[0]) / dx))
print("  drop in-lake: %s  (cell j=%d i=%d)" % (bool(mask[j0, i0]), j0, i0))
for mode in ("lake", "const"):
    fl = dict(np.load(os.path.join(PROC, "flow_tmp_e9_SE_2.5_%s.npz" % mode)))
    res = sim_drop(fl, DROP, T_h=2.0, thr_rel=0.05, n=2500)
    print("  [%s] area_km2=%.3f  centroid=(%.0f, %.0f)  theta=%.0f deg  peak0=%.3g"
          % (mode, res["area_km2"], res["centroid"][0], res["centroid"][1],
             float(res["theta"]), res["peak0"]))

print("\n== E9 summary ==")
for lab, s in summary.items():
    print("%-8s U=%.1f cd: lake=%.4g const=%.4g | |u|max %.3f vs %.3f (x%.2f) | |u|mean %.4f vs %.4f (x%.2f)"
          % (lab, s["U"], s["cd_l"], s["cd_c"], s["um_l"], s["um_c"], s["um_l"] / s["um_c"],
             s["umn_l"], s["umn_c"], s["umn_l"] / s["umn_c"]))
print("done")
