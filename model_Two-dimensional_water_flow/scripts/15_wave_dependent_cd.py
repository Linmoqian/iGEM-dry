# -*- coding: utf-8 -*-
"""E1v2: lake-appropriate wind drag coefficient vs the constant 1.3e-3 and Wu(1980).

Background (first attempt, kept in the experiment log): direct application of Zhang et al.
(2024) Eq. 11 with fetch-limited SMB EQUILIBRIUM waves collapses to Cd ~ 1.3e-4 — the
regression was calibrated on their physical-pool wave states (young wind-sea, beta* small);
equilibrium SMB waves give beta* = 7-22 (fully developed), far outside calibration.
The paper's practical findings for OUR wind range (2-3 m/s, buoyancy of light winds):
  - Cd at light winds is 1.0-3.1x the ocean-linear extrapolation (Fig. 4b; r^2=0.901 for
    1.6 < U10 <= 3.0, positive slope);
  - model (UKL) velocities with wave-dependent Cd were 57-90% higher vs Wu(1982);
  - Delft3D default Cd = 0.0025, MIKE21 uses 0.0016-0.0026 by wind range.

E1v2 uses: Cd(U) linear fit through their Fig.4b positive branch endpoints
(1.32e-3 at U=1.6 -> 3.22e-3 at U=3.0), with a mild fetch-based spatial modulation
(higher stress over open water, as found in the UKL application), then spin-ups.
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
RHO_AIR = 1.225

def cd_lake(U):
    """Zhang et al. 2024 Fig.4b positive-branch linear fit (1.6 < U <= 3.0)."""
    return float(np.clip(1.32e-3 + 1.27e-3*(U - 1.6), 1.2e-3, 3.6e-3))

def fetch_field(wind_dir_deg):
    th = np.radians(wind_dir_deg)
    o = np.array([np.sin(th), np.cos(th)])
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
    return cur

def tau_faces_fetch(U, dgr, fscale=0.35):
    """cd_cell = cd_lake(U) * (1 + fscale*(fetch/fetch_max - 0.5))"""
    F = fetch_field(dgr)
    F = np.where(mask, F, 0.0)
    Fmax = F[mask].max()
    cd = np.where(mask, cd_lake(U)*(1.0 + fscale*(F/max(Fmax, 1.0) - 0.5)), 0.0)
    th = np.radians(dgr)
    ux, uy = -np.sin(th), -np.cos(th)
    tau = RHO_AIR*cd*U**2
    tux_f = np.zeros((ny, nx+1)); tux_f[:, 1:nx] = 0.5*(tau*ux)[:, :-1] + 0.5*(tau*ux)[:, 1:]
    tuy_f = np.zeros((ny+1, nx)); tuy_f[1:ny, :] = 0.5*(tau*uy)[:-1, :] + 0.5*(tau*uy)[1:, :]
    return cd, tux_f, tuy_f, F

CFG = dict(dt=20.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode="smag")
cfg = SweConfigSI(dx=dx, **CFG)

def spin24(tau_x, tau_y, label=""):
    solver = ShallowWaterSolverSI(mask, depth, cfg)
    st = solver.init_state()
    for _ in range(int(24*3600.0/cfg.dt)):
        solver.step(st, tau_x, tau_y)
    uc, vc = cell_velocities(st)
    sp = np.sqrt(uc**2 + vc**2)
    print("%-26s |u|max=%.4f mean=%.4f" % (label, float(sp[mask].max()), float(sp[mask].mean())))
    return dict(uc=uc, vc=vc, u=st["u"], v=st["v"], eta=st["eta"], mask=mask, depth=depth, xs=xs, ys=ys, dx=dx)

results = {}
for lab, (U, dgr) in [("SE_2p5", (2.5, 135.0)), ("N_3p0", (3.0, 0.0)), ("W_2p0", (2.0, 270.0))]:
    cd, tuxf, tuyf, F = tau_faces_fetch(U, dgr)
    tuxc, tuyc, _ = wind_stress(U, dgr, cd=1.3e-3)
    tuxw, tuyw, cdw = wind_stress(U, dgr, cd_mode="wu")
    fs = spin24(tuxf, tuyf, label="%s lake-Cd(%.2f%% fetch mod)" % (lab, 100*0.35*(1/2)))
    fc = spin24(np.full((ny, nx+1), tuxc), np.full((ny+1, nx), tuyc), label="%s const Cd=1.3e-3" % lab)
    fw = spin24(np.full((ny, nx+1), tuxw), np.full((ny+1, nx), tuyw), label="%s Wu1980 Cd=%.4g" % (lab, cdw))
    results[lab] = dict(wave=fs, const=fc, wu=fw, cd=cd, F=F, U=U, dir=dgr)
    np.savez_compressed(os.path.join(PROC, "flow_%s_cdlake.npz" % lab), **fs)
    print("  %s: Cd mean=%.4g min=%.4g max=%.4g ; fetch mean=%.0f max=%.0f m"
          % (lab, cd[mask].mean(), cd[mask].min(), cd[mask].max(), F[mask].mean(), F[mask].max()))

fig, axes = plt.subplots(2, 3, figsize=(18, 8.0))
for k, lab in enumerate(["SE_2p5", "N_3p0", "W_2p0"]):
    r = results[lab]
    im = axes[0][k].pcolormesh(xs, ys, r["cd"], cmap="plasma", shading="auto")
    axes[0][k].set_title("%s: lake-Cd field (mean %.2g)" % (lab, r["cd"][mask].mean()))
    fig.colorbar(im, ax=axes[0][k], shrink=0.8)
    spw = np.sqrt(r["wave"]["uc"]**2 + r["wave"]["vc"]**2)
    spc = np.sqrt(r["const"]["uc"]**2 + r["const"]["vc"]**2)
    ratio = spw/np.maximum(spc, 1e-6)
    im2 = axes[1][k].pcolormesh(xs, ys, np.where(mask, ratio, np.nan), cmap="RdBu_r", vmin=0.7, vmax=1.8, shading="auto")
    axes[1][k].set_title("speed ratio lake-Cd/const (mean %.2f)" % np.nanmean(ratio[mask]))
    fig.colorbar(im2, ax=axes[1][k], shrink=0.8)
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig09_wave_dependent_cd.png"), dpi=130)
print("saved fig09_wave_dependent_cd.png")
