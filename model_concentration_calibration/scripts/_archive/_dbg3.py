import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 1
C, t, y = d['C'][m], d['t'][m], d['fold'][m]
# nlp at truth
p_true = dict(synth.TRIGGER_PROFILES[1]); p_true['arel']=0.05; p_true['sfloor']=0.02
z_true = fw.transform(np.array([p_true[k] for k in fw.PARAM_ORDER]))
nlp_true = cal.neg_log_post(z_true, C, t, y)
print('nlp at truth:', round(nlp_true, 2))
F = fw.forward_pts(C, t, fw.unpack(z_true))
print('truth residual RMS:', round(float(np.sqrt(np.mean((y-F)**2))), 4))
# nlp at prior-mean init
z0 = np.array([fw.PRIORS[n][0] for n in fw.PARAM_ORDER])
print('nlp at z0:', round(cal.neg_log_post(z0, C, t, y), 2))
F0 = fw.forward_pts(C, t, fw.inv_transform(z0))
print('z0 residual RMS:', round(float(np.sqrt(np.mean((y-F0)**2))), 4))
# optimize from truth
from scipy.optimize import minimize
res = minimize(cal.neg_log_post, z_true, args=(C, t, y, 1.0), method='L-BFGS-B', options={'maxiter': 3000, 'ftol': 1e-12})
print('opt from truth: nlp', round(float(res.fun), 2), 'success', res.success)
p_hat = fw.inv_transform(res.x)
print('params:', {k: round(float(v), 3) for k, v in fw.unpack(p_hat).items()})
Fh = fw.forward_pts(C, t, p_hat)
print('fitted residual RMS:', round(float(np.sqrt(np.mean((y-Fh)**2))), 4))