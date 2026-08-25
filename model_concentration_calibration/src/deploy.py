# deploy.py — edge artifact: monotone inversion lookup tables + predictor
import json
import numpy as np
import forward as fw


def build_inverse_table(p, t_nodes=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0), n=48):
    # returns {t: {'Q': [...], 'C': [...]}} monotone increasing C(Q)
    table = {}
    for t in t_nodes:
        C = np.logspace(-2.5, 2.0, n)
        F = fw.forward_pts(C, np.array([float(t)]), p)[:, 0]
        # Q must be strictly increasing in C for inversion; enforce monotone filter
        ok = np.r_[True, np.diff(F) > 1e-9]
        # drop non-monotone tail
        last = np.max(np.where(ok)[0]) + 1
        C, F = C[:last], F[:last]
        table[float(t)] = dict(Q=[float(x) for x in F], C=[float(x) for x in C])
    return table


def build_artifact(p, cal_day=None, device=None, t_nodes=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0), meta=None):
    art = dict(version='0.9', params=p, t_nodes=list(t_nodes),
               inverse=build_inverse_table(p, t_nodes),)
    if cal_day:
        art['calibration_day'] = dict(lod=cal_day['lod'], loq=cal_day['loq'], blank=cal_day['blank'])
    if device:
        art['device'] = dict(a=device['a'], b=device['b'])
    art['meta'] = meta or {}
    return art


def save_artifact(art, path):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)


def load_artifact(path):
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def predict_q2c(art, q, t, device=None):
    # q: device ratio; t: measurement time; interpolate C from lookup table
    q_bi = q
    if device:
        q_bi = (q - device['b']) / device['a']
    keys = sorted(float(k) for k in art['inverse'].keys())
    if not keys:
        return None
    t2 = float(t)
    k0, k1 = keys[0], keys[-1]
    if t2 <= k0:
        t_use = k0
    elif t2 >= k1:
        t_use = k1
    else:
        t_use = min(keys, key=lambda k: abs(k - t2))
    seg = art['inverse'][t_use] if t_use in art['inverse'] else art['inverse'][str(t_use)]
    Qarr = np.array(seg['Q']); Carr = np.array(seg['C'])
    if q_bi <= Qarr[0]:
        return float(Carr[0])
    if q_bi >= Qarr[-1]:
        return float(Carr[-1])
    return float(np.interp(q_bi, Qarr, Carr))