# -*- coding: utf-8 -*-
"""E1: wave-dependent wind drag coefficient (Zhang, Chen & Brett 2024, WRR 60:e2023WR035914)
vs constant 1.3e-3 vs Wu(1980), for the three production wind scenarios.

Wave-dependent model (their Eq. 11 + Toba et al. 1990 Charnock scaling):
  Cd = 1.956 * alpha * (U10/u*)^-1.996 * Fr_H^0.213 * Re_H^0.298
  alpha = 0.02 * beta*^0.5 ;  beta* = cp/u* ; cp = g*Ts/(2 pi)
  Fr_H = u*/sqrt(g*Hs) ; Re_H = u**Hs/nu_a ; nu_a = 1.46e-5 m2/s
Waves: fetch-limited SMB estimates per cell (fetch = along-wind distance to upwind shore);
  g*Hs/U^2 = 0.283*tanh(0.0125*X^0.42), g*Ts/(2 pi U) = 1.20*tanh(0.077*X^0.25), X = gF/U^2.
u* from fixed-point iteration: u* = U*sqrt(Cd).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.swe_si import ShallowWaterSolverSI, SweConfigSI, wind_stress
from swflow.viz import cell_velocities
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from swflow.viz import setup_style
setup_style()

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
dom = dict(np.load(os.path.join(PROC, "domain.npz")))
mask, depth, xs, ys, dx = dom["mask"], dom["depth"], dom["xs"], dom["ys"], float(dom["dx"])
ny, nx = mask.shape
G, RHO_AIR, NU_A = 9.81, 1.225, 1.46e-5

def fetch_field(wind_dir_deg):
    """along-wind fetch: distance (m) from each wet cell to the upwind shore
    (ray cast toward the wind source; waves grow over this distance)."""
    th = np.radians(wind_dir_deg)
    o = np.array([np.sin(th), np.cos(th)])  # upwind unit vector (x, y)
    jj, ii = np.where(mask)
    n = len(jj)
    posx = xs[ii] + 0.0; posy = ys[jj] + 0.0
    cur = np.zeros((ny, nx))
    for k in range(1, 60):
        posx = posx + o[0]*dx; posy = posy + o[1]*dx
        i2 = np.floor((posx - xs[0])/dx).astype(int); j2 = np.floor((posy - ys[0])/dx).astype(int)
        ok = (i2 >= 0) & (i2 < nx) & (j2 >= 0) & (j2 < ny)
        inw = np.zeros(n, bool); inw[ok] = mask[j2[ok], i2[ok]]
        still = inw & (cur[jj, ii] <= 0)
        cur[jj[still], ii[still]] = k*dx
    fetch = cur
    return fetch

def wave_dependent_cd_field(U, wind_dir_deg, cd0=1.5e-3, iters=6):
    """return (cd field ny,nx, Hs field, Ts field, tau field (tau_x,tau_y arrays at faces handled outside))"""
    F = fetch_field(wind_dir_deg)
    F = np.where(mask, np.maximum(F, 2*dx), 0.0)
    Xv = G*F/U**2
    Hs = 0.283*(U**2/G)*np.tanh(0.0125*np.power(np.maximum(Xv, 1e-6), 0.42))
    Ts = (2*np.pi*U/G)*(1.20)*np.tanh(0.077*np.power(np.maximum(Xv, 1e-6), 0.25))
    Hs = np.where(mask, Hs, 0.0); Ts = np.where(mask, Ts, 0.0)
    cd = np.where(mask, cd0, 0.0)
    for _ in range(iters):
        ustar = U*np.sqrt(cd)
        cp = G*Ts/(2*np.pi)
        beta = cp/np.maximum(ustar, 1e-6)
        alpha = 0.02*np.sqrt(np.maximum(beta, 1e-6))
        FrH = ustar/np.sqrt(G*np.maximum(Hs, 1e-4))
        ReH = ustar*Hs/NU_A
        cd_new = 1.956*alpha*np.power(U/np.maximum(ustar, 1e-6), -1.996) \
                 * np.power(np.maximum(FrH, 1e-12), 0.213) * np.power(np.maximum(ReH, 1e-12), 0.298)
        cd = np.where(mask, 0.5*(cd + cd_new), 0.0)
    return cd, Hs, Ts

def tau_faces(cd_field, U, wind_dir_deg):
    th = np.radians(wind_dir_deg)
    ux, uy = -np.sin(th), -np.cos(th)
    tau = RHO_AIR * cd_field * U**2
    tux, tuy = tau*ux, tau*uy
    tux_f = np.zeros((ny, nx+1)); tux_f[:, 1:nx] = 0.5*(tux[:, :-1] + tux[:, 1:])
    tuy_f = np.zeros((ny+1, nx)); tuy_f[1:ny, :] = 0.5*(tuy[:-1, :] + tuy[1:, :])
    return tux_f, tuy_f

CFG = dict(dt=20.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode="smag")
cfg = SweConfigSI(dx=dx, **CFG)

def spin24(tau_x, tau_y, depth_field=None, label=""):
    solver = ShallowWaterSolverSI(mask, depth_field if depth_field is not None else depth, cfg)
    st = solver.init_state()
    for _ in range(int(24*3600.0/cfg.dt)):
        solver.step(st, tau_x, tau_y)
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2 + vc**2)
    print("%-22s |u|max=%.4f mean=%.4f" % (label, float(sp[mask].max()), float(sp[mask].mean())))
    return dict(uc=uc, vc=vc, u=st["u"], v=st["v"], eta=st["eta"], mask=mask, depth=depth, xs=xs, ys=ys, dx=dx)

results = {}
for lab, (U, dgr) in [("SE_2p5", (2.5, 135.0)), ("N_3p0", (3.0, 0.0)), ("W_2p0", (2.0, 270.0))]:
    cd_w, Hs, Ts = wave_dependent_cd_field(U, dgr)
    m = mask
    print("%s: Cd field min=%.4g mean=%.4g max=%.4g  Hs mean=%.3f (max %.3f)  Ts mean=%.2f"
          % (lab, cd_w[m].min(), cd_w[m].mean(), cd_w[m].max(), Hs[m].mean(), Hs[m].max(), Ts[m].mean()))
    tuxf, tuyf = tau_faces(cd_w, U, dgr)
    tuxc, tuyc = wind_stress(U, dgr, cd=1.3e-3)[:2]
    tuxw, tuyw, cdw = wind_stress(U, dgr, cd_mode="wu")
    fs = spin24(tauxf if False else tuxf, tuyf, label="%s wave-dep Cd" % lab)
    fc = spin24(np.full((ny, nx+1), tuxc), np.full((ny+1, nx), tuyc), label="%s const Cd=1.3e-3" % lab)
    fw = spin24(np.full((ny, nx+1), tuxw), np.full((ny+1, nx), tuyw), label="%s Wu1980 Cd=%.4g" % (lab, cdw))
    results[lab] = dict(wave=fs, const=fc, wu=fw, cd=cd_w, Hs=Hs, Ts=Ts, U=U, dir=dgr)
    np.savez_compressed(os.path.join(PROC, "flow_%s_cdwav.npz" % lab), **fs)

# figure: Cd fields + speed ratios
fig, axes = plt.subplots(2, 3, figsize=(18, 8.0))
for k, lab in enumerate(["SE_2p5", "N_3p0", "W_2p0"]):
    r = results[lab]
    im = axes[0][k].pcolormesh(xs, ys, r["cd"], cmap="plasma", shading="auto")
    axes[0][k].set_title("%s: Cd field (mean %.2g)" % (lab, r["cd"][mask].mean()))
    fig.colorbar(im, ax=axes[0][k], shrink=0.8)
    spw = np.sqrt(r["wave"]["uc"]**2 + r["wave"]["vc"]**2)
    spc = np.sqrt(r["const"]["uc"]**2 + r["const"]["vc"]**2)
    ratio = spw/np.maximum(spc, 1e-6)
    im2 = axes[1][k].pcolormesh(xs, ys, np.where(mask, ratio, np.nan), cmap="RdBu_r", vmin=0.7, vmax=1.6, shading="auto")
    axes[1][k].set_title("speed ratio wave/const (mean %.2f)" % np.nanmean(ratio[mask]))
    fig.colorbar(im2, ax=axes[1][k], shrink=0.8)
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig09_wave_dependent_cd.png"), dpi=130)
print("saved fig09_wave_dependent_cd.png")
