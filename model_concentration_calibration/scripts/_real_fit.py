import sys, os, json
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import loader, calibrate as cal, forward as fw

d = loader.load()
f = loader.fold_by_time(d)
W = (f['C'] > 0) & (f['t'] >= 2.0) & (f['t'] <= 9.0)
print('fit window rows:', int(W.sum()))
results = {}
for tid in range(8):
    m = W & (f['trigger'] == tid)
    ystar = f['fold'][m]; C = f['C'][m]; t = f['t'][m]
    best = None
    for sign in (+1.0, -1.0):
        try:
            p_hat, z_hat, fun = cal.fit_train(C, t, ystar, prior_scale=1.0, amp_sign=sign, seed=tid, n_restarts=5)
        except Exception as e:
            print('trig', tid, 'sign', sign, 'ERR', e); continue
        if best is None or fun < best[2]:
            best = (p_hat, z_hat, fun, sign)
    if best is None:
        print('trigger', tid, 'FIT FAILED'); continue
    p_hat, z_hat, fun, sign = best
    F = fw.forward_points(C, t, p_hat)
    resid = ystar - F
    rms = float(np.sqrt(np.mean(resid ** 2)))
    pred = {}
    for c in [0.05,0.1,0.25,0.5,1.0,2.0,5.0]:
        for tt in [2.0,3.0,4.0,5.0,6.0,9.0]:
            sel = m & (f['C']==c) & np.isclose(f['t'], tt)
            if int(sel.sum()) == 0: continue
            obs = float(np.median(f['fold'][sel]))
            fitv = float(fw.forward_points(np.array([c]), np.array([tt]), p_hat)[0])
            pred[(c, tt)] = (obs, fitv)
    mae_med = float(np.nanmean([abs(o - v) for (o, v) in pred.values()]))
    ll = None
    if sign > 0:
        try: ll = cal.lod_loq(p_hat, 6.0)
        except Exception: ll = None
    results[tid] = dict(sign=int(sign), nlp=float(fun), rms=rms, mae_med=mae_med,
                        params={k: float(v) for k, v in p_hat.items()},
                        lod=(float(ll['lod']) if ll and ll['lod'] else None),
                        loq=(float(ll['loq']) if ll and ll['loq'] else None))
    print('trigger', tid, 'sign', int(sign), 'nlp', round(fun,1), 'rms', round(rms,3), 'mae_med', round(mae_med,3))