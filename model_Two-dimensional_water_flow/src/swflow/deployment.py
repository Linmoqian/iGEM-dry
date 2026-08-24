# -*- coding: utf-8 -*-
"""
swflow.deployment - single-drop dispersion and drone drop-point optimization.

Concept:
  A drone releases a payload of engineered degradation bacteria at point p0 at t=0.
  The payload immediately spreads over a small mixing radius (sigma0) and is then
  advected/diffused by the wind-driven lake circulation (depth-averaged 2D flow).
  The "effective coverage" at time t is the lake area where the local areal dose
  stays above a required threshold C_req (normalized by the initial peak):
      coverage(t) = { x : C(x,t) >= thr_rel * C_peak(t=0) }
  For a set of candidate drop points, and an ensemble of plausible wind scenarios,
  we maximize the expected protected fraction of a target bloom patch.
"""
import numpy as np
from .particles import ParticleTracer

# surface wind-drift fraction (E3 experiment): area robust, position sensitive -> default 2%
WINDAGE_DEFAULT = 0.02
# m6-equivalent degradation kinetics anchors (Toxins 2018, 10:536 fig.3b, as used by
# the MC-LR degradation module prototype; ratios relative to 30 C)
_K_T_ANCHOR = {20.0: 1.67, 30.0: 3.33, 37.0: 2.00, 40.0: 0.05}
_K_REF = 0.25  # h^-1, m6-equivalent at D=1, 30 C, pH7
_C_GOAL = 1.0  # ug/L, WHO guideline target

def wind_vec_from_flow(flow):
    """wind velocity vector (m/s, direction the air moves toward) from a flow dict."""
    if "wind_mps" not in flow or "wind_dir" not in flow:
        return None
    th = np.radians(float(flow["wind_dir"]))
    return np.array([-np.sin(th), -np.cos(th)]) * float(flow["wind_mps"])

def k_eff(T_C, D=1.0):
    """effective first-order rate k(T) = 0.25 * f_T(T) [h^-1] per m6-equivalent density D."""
    pts = _K_T_ANCHOR
    keys = sorted(pts)
    T = float(T_C)
    if T in pts:
        r = pts[T]/pts[30.0]
    else:
        Tt = np.clip(T, keys[0], keys[-1])
        r = np.exp(np.interp(Tt, keys, np.log([pts[v] for v in keys])))/pts[30.0]
    return _K_REF*max(float(r), 0.0)*D

def physical_thr_rel(C0=2.85, t_ok=24.0, T_water=25.0, M=1.0):
    """Physical coverage threshold thr_rel = C_req / B_peak0 (E4 experiment).
    C0: initial MC-LR [ug/L]; t_ok: allowed treatment time [h]; T_water: temperature [C];
    M: initial peak at the drop centre in multiples of the m6 reference density.
    Requires C0 > C_GOAL (no treatment needed otherwise; returns 0)."""
    if float(C0) <= _C_GOAL:
        return 0.0
    D_req = np.log(float(C0)/_C_GOAL)/(k_eff(T_water)*float(t_ok))
    return float(D_req/max(float(M), 1e-9))

def make_tracer(flow, dx, rng_seed=7, w_a=WINDAGE_DEFAULT):
    return ParticleTracer(flow['uc'], flow['vc'], flow['mask'], flow['xs'], flow['ys'],
                          dx=float(dx), rng=np.random.default_rng(rng_seed),
                          wind_vec=wind_vec_from_flow(flow), w_a=w_a)

def release_positions(drop_xy, n, sigma0, rng):
    x0, y0 = drop_xy
    x = x0 + sigma0*rng.standard_normal(n)
    y = y0 + sigma0*rng.standard_normal(n)
    return np.column_stack([x, y])

def sim_drop(flow, drop_xy, T_h=1.0, dt=5.0, D=0.3, n=2000, sigma0=25.0,
             thr_rel=0.05, rng_seed=7, record=False, w_a=WINDAGE_DEFAULT):
    """advect one release; return field + area covered at the end + diagnostics
    (windage = w_a * wind applied unless flow carries no wind info; thr_rel is a
    RELATIVE threshold — for a physical threshold use deployment.physical_thr_rel)."""
    tr = make_tracer(flow, flow.get('dx', 50.0), rng_seed=rng_seed, w_a=w_a)
    pos0 = release_positions(drop_xy, n, sigma0, tr.rng)
    pos_end, traj = tr.run(pos0, T_h*3600.0, dt=dt, D=D, record=record)
    C = tr.density(pos_end, sigma_m=30.0)
    # reference peak at t0
    C0 = tr.density(pos0, sigma_m=30.0)
    peak0 = float(C0.max())
    thr = thr_rel*peak0
    cov = (C >= thr) & flow['mask']
    dx = float(flow['xs'][1]-flow['xs'][0])
    area_cov = float(cov.sum()*dx*dx)
    cxy = pos_end.mean(axis=0)
    var_e, theta = None, None
    if n > 1:
        X = pos_end - cxy
        covm = (X.T @ X)/(n-1)
        w, vec = np.linalg.eigh(covm)
        var_e = w
        theta = np.degrees(np.arctan2(vec[1, np.argmax(w)], vec[0, np.argmax(w)]))
    res = {'C': C, 'cov': cov, 'area_km2': area_cov/1e6, 'centroid': cxy,
           'eig_var': var_e, 'theta': theta, 'peak0': peak0, 'thr': thr,
           'pos_end': pos_end, 'traj': traj, 'drop_xy': np.asarray(drop_xy, float)}
    return res

def batch_sim_drops(flow, drops, T_h=1.0, dt=5.0, D=0.3, n=800, sigma0=25.0,
                    thr_rel=0.05, rng_seed=7, w_a=WINDAGE_DEFAULT):
    """all candidates in one vectorized run; returns per-candidate coverage & centroid.
    (windage applied; thr_rel stays a relative threshold — see physical_thr_rel.)"""
    drops = np.asarray(drops, float)
    k = drops.shape[0]
    tr = make_tracer(flow, flow.get('dx', 50.0), rng_seed=rng_seed, w_a=w_a)
    # release all swarms together: offset groups (keep the ACTUAL initial groups
    # so the peak threshold is computed from the same realization that was advected)
    pos0 = np.vstack([release_positions(drops[i], n, sigma0, tr.rng) for i in range(k)])
    pos_end, _ = tr.run(pos0, T_h*3600.0, dt=dt, D=D)
    dx = float(flow['xs'][1]-flow['xs'][0])
    out = []
    for i in range(k):
        grp = pos_end[i*n:(i+1)*n]
        grp0 = pos0[i*n:(i+1)*n]
        C = tr.density(grp, sigma_m=30.0)
        C0 = tr.density(grp0, sigma_m=30.0)
        thr = thr_rel*float(C0.max())
        cov = (C >= thr) & flow['mask']
        out.append((float(cov.sum()*dx*dx/1e6), grp.mean(axis=0), C, cov))
    return out

def bloom_patch(mask, xs, ys, cx, cy, rx, ry, theta_deg=0.0):
    """elliptical bloom patch mask on the grid"""
    XX, YY = np.meshgrid(xs, ys)
    t = np.radians(theta_deg)
    xr = (XX-cx)*np.cos(t) + (YY-cy)*np.sin(t)
    yr = -(XX-cx)*np.sin(t) + (YY-cy)*np.cos(t)
    return mask & ((xr/rx)**2 + (yr/ry)**2 <= 1.0)
