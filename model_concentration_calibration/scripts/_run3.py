import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw

d = synth.gen_dataset(seed=42)
print('rows:', len(d['C']))
def fmt(x):
    return 'None' if x is None else round(float(x), 4)
for tid, sign in [(1, 1), (5, 1), (6, 1), (7, -1)]:
    m = d['trigger'] == tid
    p_hat, z_hat, fun = cal.fit_train(d['C'][m], d['t'][m], d['fold'][m], prior_scale=1.0, amp_sign=sign)
    print('trigger %d: nlp=%.2f  Amax=%.3f  K0=%.2f  Kf=%.2f  tauA=%.2f  tauD=%.1f' % (
        tid, fun, p_hat['Amax'], p_hat['K0'], p_hat['Kf'], p_hat['tauA'], p_hat['tauD']))
    ll = cal.lod_loq(p_hat, 6.0)
    print('  LOD=%s  LOQ=%s  blank_sd=%.3f' % (fmt(ll['lod']), fmt(ll['loq']), ll['blank_sd']))