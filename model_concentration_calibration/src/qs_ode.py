"""
qs_ode.py — 生物传感模块的机理仿真（用于生成先验/合成数据）
============================================================================
模型结构（简化但保留关键动力学）：
  靶标感应:   s(C)      = Hill(C; Kd_eff, n_apt)
  AHL池:      dA/dt     = kL * N * s(C) * (1 + b * Hill(A; Ka, na)) - gamma_A * A
  GFP:        dG/dt     = kG * Hill(A; Ka, na) - lam * G ; dGm/dt = kMatG * (G - Gm)
  RFP:        dR/dt     = kR - lam * R                 ; dRm/dt = kMatR * (R - Rm)
  Q(t) = Gm / Rm
所有单位：浓度 μg/L；时间 min。
"""
import numpy as np
from scipy.integrate import solve_ivp


def hill(x, k, n):
    x = np.asarray(x, dtype=float)
    return x ** n / (k ** n + x ** n + 1e-12)


DEFAULT = dict(
    Kd_eff=3.0,          # ug/L: effective switch EC50 (aptamer Kd x toehold coupling)
    n_apt=1.6,           # sensing cascade effective Hill
    kL=0.9,              # AHL synthesis rate
    N_cells=1.0,         # normalized cell density (batch covariate)
    b=25.0,              # positive feedback strength (Plux-driven luxI amplification)
    Ka=0.15,             # ug/L: LuxR-AHL activation EC50 of Plux (effective)
    na=2.0,              # QS feedback effective Hill
    gamma_A=0.02,        # AHL loss
    kG=1.0,              # GFP max synthesis (normalized)
    kG0=0.02,            # basal GFP leak (normalized)
    kR=0.6,              # RFP constitutive synthesis (normalized)
    lam=0.012,           # dilution rate (min^-1)
    kMatG=0.14,          # sfGFP maturation (t1/2 ~ 5 min)
    kMatR=0.0077,        # TurboRFP maturation (t1/2 ~ 90 min, FPbase)
)


def simulate(C, tmax=1440.0, npts=241, params=None):
    p = {**DEFAULT, **(params or {})}
    if np.isscalar(C):
        C = [C]
    t = np.linspace(0.0, tmax, npts)
    out = np.zeros((len(C), npts))
    for i, c in enumerate(C):
        s = 0.0 if c <= 0 else hill(c, p['Kd_eff'], p['n_apt'])

        def rhs(tau, y):
            A, G, Gm, R, Rm = y
            feed = hill(max(A, 0.0), p['Ka'], p['na'])
            dA = p['kL'] * p['N_cells'] * s * (1.0 + p['b'] * feed) - p['gamma_A'] * A
            dG = p['kG0'] + p['kG'] * feed - p['lam'] * G
            dGm = p['kMatG'] * (G - Gm)
            dR = p['kR'] - p['lam'] * R
            dRm = p['kMatR'] * (R - Rm)
            return [dA, dG, dGm, dR, dRm]

        sol = solve_ivp(rhs, [0.0, tmax], [0.0, 0.0, 0.0, 0.0, 0.0],
                        t_eval=t, method='LSODA', rtol=1e-8, atol=1e-10)
        Gm, Rm = sol.y[2], sol.y[4]
        out[i] = Gm / np.clip(Rm, 1e-9, None)
    return t, (out[0] if len(C) == 1 else out)


def effective_curve(C, t, params=None):
    tt, Q = simulate(C, tmax=float(np.max(t)) + 1.0, npts=200, params=params)
    if Q.ndim == 1:
        return np.interp(t, tt, Q)
    return np.array([np.interp(t, tt, Q[i]) for i in range(Q.shape[0])])