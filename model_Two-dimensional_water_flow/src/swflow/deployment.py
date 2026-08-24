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

def make_tracer(flow, dx, rng_seed=7):
    return ParticleTracer(flow['uc'], flow['vc'], flow['mask'], flow['xs'], flow['ys'],
                          dx=float(dx), rng=np.random.default_rng(rng_seed))

def release_positions(drop_xy, n, sigma0, rng):
    x0, y0 = drop_xy
    x = x0 + sigma0*rng.standard_normal(n)
    y = y0 + sigma0*rng.standard_normal(n)
    return np.column_stack([x, y])

def sim_drop(flow, drop_xy, T_h=1.0, dt=5.0, D=0.3, n=2000, sigma0=25.0,
             thr_rel=0.05, rng_seed=7, record=False):
    """advect one release; return field + area covered at the end + diagnostics"""
    tr = make_tracer(flow, flow.get('dx', 50.0), rng_seed=rng_seed)
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
                    thr_rel=0.05, rng_seed=7):
    """all candidates in one vectorized run; returns per-candidate coverage & centroid."""
    drops = np.asarray(drops, float)
    k = drops.shape[0]
    tr = make_tracer(flow, flow.get('dx', 50.0), rng_seed=rng_seed)
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
