import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal
d = synth.gen_dataset(seed=42)
ENV = (-1.9, 1.2)
for tid, sign in [(1,1),(5,1),(6,1)]:
    m = d['trigger'] == tid
    rows = []
    for b in [0,1,2]:
        tr = m & (d['batch'] != b); te = m & (d['batch'] == b)
        p_hat, z_hat, fun = cal.fit_train(d['C'][tr], d['t'][tr], d['fold'][tr], amp_sign=sign)
        draws = cal.laplace_samples(z_hat, d['C'][tr], d['t'][tr], d['fold'][tr], n_samples=300, seed=7+b, amp_sign=sign)
        sel = te & (d['t'] == 6.0)
        idx = np.where(sel)[0]
        for i in idx:
            invf = cal.invert_posterior(draws, 6.0, float(d['fold'][i]), c_prior=ENV)
            invn = cal.invert_posterior(draws, 6.0, float(d['fold'][i]), c_prior=None)
            rows.append((float(d['C'][i]), invf['median'], invf['lo5'], invf['hi95'], invf['p_ge_1'], invn['median'], invn['p_ge_1']))
    arr = np.array(rows)
    y = arr[:,0]; mf = arr[:,1]; lo = arr[:,2]; hi = arr[:,3]; p1 = arr[:,4]; mn = arr[:,5]
    pos = y > 0
    mael = float(np.mean(np.abs(np.log10(np.clip(mf[pos]/y[pos],1e-6,1e6)))))
    cover = float(np.mean((y>=lo)&(y<=hi)))
    from sklearn.metrics import roc_auc_score
    lab = (y>=1).astype(int)
    auc = float(roc_auc_score(lab, p1))
    mael_n = float(np.mean(np.abs(np.log10(np.clip(mn[pos]/y[pos],1e-6,1e6)))))
    print(f'trigger {tid}: n={len(y)} env: MAE={mael:.3f} cov90={cover:.3f} AUC={auc:.3f} | flat: MAE={mael_n:.3f}')
    print('   medians by C:', [round(float(np.median(mf[y==c])),2) for c in [0.05,0.25,0.5,1,2,5,10]])