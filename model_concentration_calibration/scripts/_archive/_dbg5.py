import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 1
C, t, y = d['C'][m], d['t'][m], d['fold'][m]
p_true = dict(synth.TRIGGER_PROFILES[1]); p_true['arel']=0.05; p_true['sfloor']=0.02
F = fw.forward_pts(C, t, p_true)
print('truth RMS:', round(float(np.sqrt(np.mean((y - F)**2))), 4))
vals = np.array([p_true[k] for k in fw.PARAM_ORDER])
z = fw.transform(vals)
back = fw.inv_transform(z)
print('roundtrip maxdiff:', round(float(np.max(np.abs(vals - back))), 6))
print('nlp at z:', round(cal.neg_log_post(z, C, t, y), 2))
print('nlp at truth-as-z-check:', round(cal.neg_log_post(z, C, t, y, 1.0), 2))
from scipy.optimize import minimize
res = minimize(cal.neg_log_post, z, args=(C, t, y, 1.0), method='L-BFGS-B', options={'maxiter': 5000, 'ftol': 1e-15, 'gtol': 1e-8})
print('opt: fun', round(float(res.fun), 2), 'nit', res.nit, 'success', res.success)