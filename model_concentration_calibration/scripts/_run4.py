import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
print('rows:', len(d['C']))
results = {}
for tid, sign in [(1, 1), (5, 1), (6, 1), (7, -1)]:
    m = d['trigger'] == tid
    p_hat, z_hat, fun = cal.fit_train(d['C'][m], d['t'][m], d['fold'][m], prior_scale=1.0, amp_sign=sign)
    print(f'trigger {tid}: nlp={fun:.2f}')
    print('  fit:', {k: round(float(v), 3) for k, v in p_hat.items()})
    print('  tru:', {k: round(float(v), 3) for k, v in synth.TRIGGER_PROFILES[tid].items()})
    ll = cal.lod_loq(p_hat, 6.0)
    fmt = lambda x: 'None' if x is None else round(float(x), 4)
    print(f'  LOD={fmt(ll["lod"])} LOQ={fmt(ll["loq"])} blank_sd={ll["blank_sd"]:.3f}')
    if sign > 0:
        draws = cal.laplace_samples(z_hat, d['C'][m], d['t'][m], d['fold'][m], n_samples=400, seed=3, amp_sign=sign)
        for c_true in [0.1, 0.5, 1.0, 2.0]:
            mm = m & (d['C'] == c_true) & (d['t'] == 6.0)
            q = float(d['fold'][mm][0])
            inv = cal.invert_posterior(draws, 6.0, q)
            print(f'    C={c_true}: fold={q:.3f} med={inv["median"]:.3f} CI=[{inv["lo5"]:.3f},{inv["hi95"]:.3f}] P>=1={inv["p_ge_1"]:.3f}')
    results[tid] = (p_hat, z_hat)