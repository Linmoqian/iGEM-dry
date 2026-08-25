import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, evaluate as ev, qs_ode, forward as fw

d = synth.gen_dataset(seed=42, want_truth=True)
print('rows:', len(d['C']))
p_hat, z_hat, fun = cal.fit_train(d['C'], d['t'], d['Q'], prior_scale=1.0)
p = fw.unpack(p_hat)
print('fit nlp:', round(fun, 2))
print('params:', {k: round(v, 4) for k, v in p.items()})
print('log params:', {k: round(np.log(p[k]), 3) for k in ['Amax','K0','Kf','tauA','tauD','tauK','arel','sfloor']})
draws = cal.laplace_samples(z_hat, d['C'], d['t'], d['Q'], n_samples=400, seed=3)
print('laplace draws ok, std of K0 log:', round(float(np.std(np.log(draws[:, fw.IDX['K0']]))), 3))
for c_true, tq in [(1.0, 4.0), (2.0, 4.0), (0.3, 4.0), (1.0, 6.0), (0.05, 6.0)]:
    mask = (d['C'] == c_true) & (np.isclose(d['t'], tq))
    q = float(d['Q'][mask][0])
    inv = cal.invert_posterior(draws, tq, q)
    print(f'C_true={c_true} t={tq}: med={inv["median"]:.3f} CI=[{inv["lo5"]:.3f},{inv["hi95"]:.3f}] P>=1={inv["p_ge_1"]:.3f}')
ll = cal.lod_loq(p, 6.0)
print('LOD/LOQ t=6:', ll)