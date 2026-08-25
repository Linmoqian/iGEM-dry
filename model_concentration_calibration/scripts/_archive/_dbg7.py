import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 1
C, t, y = d['C'][m], d['t'][m], d['fold'][m]
# truth check
p_true = dict(synth.TRIGGER_PROFILES[1]); p_true['arel']=0.05; p_true['sfloor']=0.02
vals = np.array([p_true[k] for k in fw.PARAM_ORDER])
z_true = fw.transform(vals)
print('nlp truth:', round(cal.neg_log_post(z_true, C, t, y, 1.0, 1.0), 2))
# fitted check
p_fit, z_hat, fun = cal.fit_train(C, t, y, prior_scale=1.0, amp_sign=1.0)
print('fit fun:', round(fun, 2))
p = fw.unpack(fw.inv_transform(z_hat))
p['Amax'] *= 1.0
F = fw.forward_pts(C, t, p)
s = fw.sigma_of(F, p)
print('fit resid: min', round(float(np.nanmin(y-F)),4), ' max', round(float(np.nanmax(y-F)),4), ' rms', round(float(np.sqrt(np.nanmean((y-F)**2))),4))
print('F range:', round(float(np.nanmin(F)),4), round(float(np.nanmax(F)),4), ' s range:', round(float(np.nanmin(s)),5), round(float(np.nanmax(s)),5))
print('any nan F:', bool(np.isnan(F).any()), 'any nan s:', bool(np.isnan(s).any()), 'any inf:', bool(np.isinf(F).any()))
nll = 0.5 * np.sum(((y-F)/s)**2 + np.log(2*np.pi*s**2))
nlp = float(nll - fw.prior_logp(z_hat))
print('recomputed nlp:', round(nlp, 2), ' nll:', round(float(nll), 2), ' prior:', round(float(fw.prior_logp(z_hat)), 2))