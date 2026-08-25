import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 1
C, t, y = d['C'][m], d['t'][m], d['fold'][m]
p_true = dict(synth.TRIGGER_PROFILES[1]); p_true['arel']=0.05; p_true['sfloor']=0.02
vals = np.array([p_true[k] for k in fw.PARAM_ORDER])
z_true = fw.transform(vals)
p_back = fw.unpack(fw.inv_transform(z_true))
print('roundtrip ok:', all(abs(p_back[k]-p_true[k]) < 1e-9 for k in p_true))
print('p_back:', {k: round(float(v),4) for k, v in p_back.items()})
F = fw.forward_pts(C, t, p_back)
print('truth resid rms:', round(float(np.sqrt(np.mean((y-F)**2))), 4))
s = fw.sigma_of(F, p_back)
z = (y-F)/s
print('z stats: mean', round(float(z.mean()),3), 'rms', round(float(np.sqrt(np.mean(z**2))),3), 'max', round(float(z.max()),3))
nll = 0.5*np.sum(z**2 + np.log(2*np.pi*s**2))
print('nll:', round(float(nll),2), 'prior:', round(float(fw.prior_logp(z_true)),2))