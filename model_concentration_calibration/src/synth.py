# synth.py — v3: synthetic dataset in fold space from trigger-specific profiles
import numpy as np
import forward as fw

# expected kinetics per trigger (fold-amplitude A(t), EC50 K(t), Hill n(t)); units: ug/L, HOURS
TRIGGER_PROFILES = {
    1: dict(Amax=0.42, tauA=3.3, tauD=500.0, K0=3.5, Kf=0.55, tauK=3.67, n0=1.1, n1=0.9, tauN=3.3),
    5: dict(Amax=0.75, tauA=1.5, tauD=15.0, K0=2.5, Kf=0.35, tauK=2.5, n0=1.0, n1=1.0, tauN=2.0),
    6: dict(Amax=0.60, tauA=2.0, tauD=42.0, K0=1.4, Kf=0.25, tauK=1.67, n0=1.2, n1=1.4, tauN=1.67),
    7: dict(Amax=-0.12, tauA=2.0, tauD=330.0, K0=0.8, Kf=0.4, tauK=1.67, n0=1.0, n1=0.2, tauN=1.67),
}

CONCS = np.array([0.0, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0])
TIMES = np.array([0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 9.0])


def gen_dataset(trigger_ids=(1, 5, 6, 7), concs=CONCS, times=TIMES, n_reps=3, n_batches=3,
                rel_noise=0.05, floor_noise=0.02, batch_ampl=0.15, batch_off=0.03,
                seed=42, profiles=None):
    rng = np.random.default_rng(seed)
    rows = []
    profs = profiles or TRIGGER_PROFILES
    for tid in trigger_ids:
        p = dict(profs[tid])
        p['arel'] = rel_noise
        p['sfloor'] = floor_noise
        # true fold surface
        F = fw.forward_pts(concs, times, p)  # (nc, nt)
        for bi in range(n_batches):
            amul = 1.0 + rng.normal(0, batch_ampl)
            off = rng.normal(0, batch_off)
            for ci, c in enumerate(concs):
                for ti, tv in enumerate(times):
                    for r in range(n_reps):
                        mu = 1.0 + amul * (F[ci, ti] - 1.0) + off
                        s = np.sqrt((rel_noise * mu) ** 2 + floor_noise ** 2)
                        y = max(mu + rng.normal(0, s), 0.1)
                        rows.append((int(tid), float(c), float(tv), float(y), int(bi), r))
    arr = np.array(rows, dtype=float)
    return dict(trigger=arr[:, 0].astype(int), C=arr[:, 1], t=arr[:, 2], fold=arr[:, 3],
                batch=arr[:, 4].astype(int), rep=arr[:, 5].astype(int))


def surface(tid, concs=CONCS, times=TIMES, profiles=None):
    p = dict((profiles or TRIGGER_PROFILES)[tid])
    p['arel'] = 0.05; p['sfloor'] = 0.02
    return fw.forward_pts(concs, times, p)