import sys, json
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
from scipy.stats import norm
import loader, calibrate as cal, forward as fw

d = loader.load()
f = loader.fold_by_time(d)
W = (f['C'] > 0) & (f['t'] >= 2.0) & (f['t'] <= 9.0)
res = {}
for tid, sign in [(0,1),(1,1),(5,1),(6,1),(2,-1),(3,-1),(4,-1),(7,-1)]:
    m = W & (f['trigger'] == tid)
    C, t, y = f['C'][m], f['t'][m], f['fold'][m]
    p_hat, z_hat, fun = cal.fit_train(C, t, y, amp_sign=float(sign), seed=tid, n_restarts=6)
    F = fw.forward_points(C, t, p_hat)
    rms = float(np.sqrt(np.mean((y - F)**2)))
    ll = None
    if sign > 0:
        try:
            ll = cal.lod_loq(p_hat, 6.0)
            ll = dict(lod=(float(ll['lod']) if ll['lod'] else None), loq=(float(ll['loq']) if ll['loq'] else None), blank_sd=float(ll['blank_sd']))
        except Exception as e:
            ll = None
    # leave-one-replicate-out: median-based MAE (fold space)
    preds = {}
    for rep in [1,2,3]:
        tr = m & (f['rep'] != rep)
        p2, z2, f2 = cal.fit_train(f['C'][tr], f['t'][tr], f['fold'][tr], amp_sign=float(sign), seed=tid+10, n_restarts=4)
        te = m & (f['rep'] == rep)
        F2 = fw.forward_points(f['C'][te], f['t'][te], p2)
        preds[rep] = float(np.mean(np.abs(F2 - f['fold'][te])))
    res[tid] = dict(sign=sign, nlp=fun, rms=rms, mae_rep_mean=float(np.mean(list(preds.values()))),
                    lod=(ll or {}).get('lod'), loq=(ll or {}).get('loq'), blank_sd=(ll or {}).get('blank_sd'),
                    params=p_hat, fun=fun)
    print(f'trig{tid} [{sign}] rms={rms:.4f} mae_loco={float(np.mean(list(preds.values()))):.4f} lod={(ll or {}).get("lod")}')
    print('   Amax=%.3f K0=%.3f Kf=%.3f n0=%.3f n1=%.3f tauA=%.2f tauD=%.1f tauK=%.2f tauN=%.2f arel=%.3f sfloor=%.3f' % (
        p_hat['Amax'], p_hat['K0'], p_hat['Kf'], p_hat['n0'], p_hat['n1'], p_hat['tauA'], p_hat['tauD'], p_hat['tauK'], p_hat['tauN'], p_hat['arel'], p_hat['sfloor']))
with open('D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/data/processed/real_fit_results.json','w') as fh:
    json.dump({str(k): {kk: vv for kk, vv in v.items() if kk != 'params'} for k, v in res.items()}, fh, indent=1)
# fusion demo on trigger5 C=1.0 using 2/4/6h
m5 = W & (f['trigger']==5)
p5, z5, f5 = cal.fit_train(f['C'][m5], f['t'][m5], f['fold'][m5], amp_sign=1.0, seed=5)
draws = cal.laplace_samples(z5, f['C'][m5], f['t'][m5], f['fold'][m5], n_samples=400, seed=5)
def qq(c, t):
    sel = m5 & (f['C']==c) & np.isclose(f['t'], t)
    return float(np.median(f['fold'][sel]))
grid = np.linspace(-2.5, 2.0, 231); Cg = 10**grid
def postO(pairs, env=(-1.9, 1.2)):
    lp = np.zeros(len(Cg))
    for p in draws:
        pt = fw.unpack(p)
        for (tq, qv) in pairs:
            F = fw.forward_points(Cg, np.full(len(Cg), tq), pt)
            s = fw.sigma_of(F, pt)
            lp = lp + norm.logpdf(qv, F, s)
    lp = lp/len(draws) + norm.logpdf(np.log(Cg), env[0], env[1])
    lp = lp - lp.max()
    pC = np.exp(lp); pC /= pC.sum()
    cdf = np.cumsum(pC)
    return float(Cg[np.searchsorted(cdf,0.5)]), float(Cg[np.searchsorted(cdf,0.05)]), float(Cg[np.searchsorted(cdf,0.95)]), float(pC[Cg>=1].sum())
for lab, pairs in [('2h', [(2.0, qq(1.0,2.0))]), ('4h', [(4.0, qq(1.0,4.0))]), ('2+4+6h', [(2.0, qq(1.0,2.0)), (4.0, qq(1.0,4.0)), (6.0, qq(1.0,6.0))])]:
    md, lo, hi, p1 = postO(pairs)
    print(f'trigger5 real C=1: {lab}: med={md:.3f} CI=[{lo:.3f},{hi:.3f}] P>=1={p1:.3f}')