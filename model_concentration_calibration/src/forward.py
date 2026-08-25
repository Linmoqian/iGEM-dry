# forward.py — parametric forward model (v3: fold-change form)
# Fold(C,t) = Q(C,t)/Q0(t) = 1 + A(t) * Hill(C; K(t), n(t))
#   A(t) = Amax * (1 - exp(-t/tauA)) * exp(-t/tauD)      (rise then slow decay; A can be <0 for negative triggers)
#   K(t) = Kf + (K0 - Kf) * exp(-t/tauK)                 (EC50 falls as amplification accumulates)
#   n(t) = n0 + n1 * (1 - exp(-t/tauN))                  (ultrasensitivity grows with positive feedback)
# theta (11): Amax, tauA, tauD, K0, Kf, tauK, n0, n1, tauN, arel, sfloor
# noise on fold y: sigma^2 = (arel * y)^2 + sfloor^2
import numpy as np
from scipy.special import expit


def hill(x, k, n):
    x = np.asarray(x, dtype=float)
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        z = n * (np.log(np.clip(x, 1e-30, None)) - np.log(np.clip(k, 1e-30, None)))
    return expit(z)


PARAM_ORDER = ['Amax', 'tauA', 'tauD', 'K0', 'Kf', 'tauK', 'n0', 'n1', 'tauN', 'arel', 'sfloor']
LOG_PARAMS = {'Amax', 'tauA', 'tauD', 'K0', 'Kf', 'tauK', 'tauN', 'arel', 'sfloor'}
IDX = {name: i for i, name in enumerate(PARAM_ORDER)}

# natural-scale bounds for log params; note Amax range covers negative (use sign * log|A|)
BOUNDS = dict(
    Amax=(0.005, 2.5), tauA=(0.5, 24.0), tauD=(6.0, 2000.0),
    K0=(0.05, 50.0), Kf=(0.01, 20.0), tauK=(0.5, 24.0),
    n0=(0.3, 3.0), n1=(-0.5, 3.0), tauN=(0.5, 24.0),
    arel=(0.002, 0.6), sfloor=(5e-4, 0.6),
)

# priors mean/sd in transformed space; time unit = HOURS
PRIORS = dict(
    Amax=(-0.9, 0.9),      # log|A| typical ~0.4 positive amplitude
    tauA=(1.2, 0.7), tauK=(1.25, 0.7), tauN=(1.2, 0.7),
    tauD=(5.7, 1.0),
    K0=(1.0, 0.45), Kf=(-0.5, 0.6),
    n0=(1.0, 0.3), n1=(0.6, 0.5),
    arel=(-2.7, 0.5), sfloor=(-3.5, 0.5),
)


def unpack(theta):
    return {name: theta[i] for i, name in enumerate(PARAM_ORDER)}


def transform(theta):
    t = np.asarray(theta, dtype=float).copy()
    for i, name in enumerate(PARAM_ORDER):
        if name in LOG_PARAMS:
            lo, hi = BOUNDS[name]
            v = np.clip(t[i], lo + 1e-9, hi - 1e-9)
            t[i] = np.log(v)
    return t


def inv_transform(z):
    t = np.asarray(z, dtype=float).copy()
    for i, name in enumerate(PARAM_ORDER):
        lo, hi = BOUNDS[name]
        if name in LOG_PARAMS:
            v = np.exp(np.clip(t[i], -40.0, 40.0))
            t[i] = np.clip(v, lo, hi)
        else:
            t[i] = np.clip(t[i], lo, hi)
    return t


def forward_pts(C, t, p):
    if not isinstance(p, dict):
        p = unpack(p)
    C = np.atleast_1d(np.asarray(C, dtype=float))
    t = np.atleast_1d(np.asarray(t, dtype=float))
    A = p['Amax'] * (1.0 - np.exp(-t / p['tauA'])) * np.exp(-t / p['tauD'])
    K = p['Kf'] + (p['K0'] - p['Kf']) * np.exp(-t / p['tauK'])
    n = p['n0'] + p['n1'] * (1.0 - np.exp(-t / p['tauN']))
    z = n[None, :] * (np.log(np.clip(C[:, None], 1e-30, None)) - np.log(np.clip(K[None, :], 1e-30, None)))
    return 1.0 + A[None, :] * expit(z)


def forward_points(C, t, p):
    """pointwise evaluation for paired arrays (n,) (n,)"""
    if not isinstance(p, dict):
        p = unpack(p)
    C = np.asarray(C, dtype=float)
    t = np.asarray(t, dtype=float)
    A = p['Amax'] * (1.0 - np.exp(-t / p['tauA'])) * np.exp(-t / p['tauD'])
    K = p['Kf'] + (p['K0'] - p['Kf']) * np.exp(-t / p['tauK'])
    n = p['n0'] + p['n1'] * (1.0 - np.exp(-t / p['tauN']))
    z = n * (np.log(np.clip(C, 1e-30, None)) - np.log(np.clip(K, 1e-30, None)))
    return 1.0 + A * expit(z)


def sigma_of(F, p):
    if not isinstance(p, dict):
        p = unpack(p)
    return np.sqrt((p['arel'] * F) ** 2 + p['sfloor'] ** 2)


def prior_logp(z, scale=1.0):
    t = inv_transform(z)
    lp = 0.0
    for i, name in enumerate(PARAM_ORDER):
        mu, sd = PRIORS[name]
        if name in LOG_PARAMS:
            x = np.log(np.clip(t[i], 1e-9, None))
        else:
            x = t[i]
        lp += -0.5 * ((x - mu) / (sd * scale)) ** 2
    return lp