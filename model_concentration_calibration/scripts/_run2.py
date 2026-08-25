import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
# quick sanity: generate and inspect
d = synth.gen_dataset(seed=42)
print('rows:', len(d['C']))
for tid in [1, 5, 6, 7]:
    m = d['trigger'] == tid
    print(f'trigger {tid}: n={m.sum()} fold range [{d["fold"][m].min():.3f},{d["fold"][m].max():.3f}]')
# fit trigger 1
m = d['trigger'] == 1
p_hat, z_hat, fun = cal.fit_train(d['C'][m], d['t'][m], d['fold'][m], prior_scale=1.0)
p = fw.unpack(p_hat)
print('trig1 fit nlp:', round(fun, 1))
print('trig1 fitted:', {k: round(float(v), 3) for k, v in p.items()})
print('trig1 truth :', {k: round(float(v), 3) for k, v in synth.TRIGGER_PROFILES[1].items()})
# LOD/LOQ at t=6
ll = cal.lod_loq(p, 6.0)
print('LOD/LOQ t=6:', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in ll.items()})
# inversion sanity at several true concs
draws = cal.laplace_samples(z_hat, d['C'][m], d['t'][m], d['fold'][m], n_samples=500, seed=3)
for c_true in [0.1, 0.5, 1.0, 2.0]:
    mm = m & (d['C'] == c_true) & (d['t'] == 6.0)
    q = float(d['fold'][mm][0])
    inv = cal.invert_posterior(draws, 6.0, q)
    print(f'  C={c_true}: obs_fold={q:.3f} med={inv["median"]:.3f} CI=[{inv["lo5"]:.3f},{inv["hi95"]:.3f}] P>=1={inv["p_ge_1"]:.3f}')