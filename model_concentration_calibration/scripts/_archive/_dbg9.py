import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 1
C, t, y = d['C'][m], d['t'][m], d['fold'][m]
p_true = dict(synth.TRIGGER_PROFILES[1]); p_true['arel']=0.05; p_true['sfloor']=0.02
F = fw.forward_pts(C, t, p_true)
print('F[:5]:', np.round(F[:5],4))
print('y[:5]:', np.round(y[:5],4))
s = fw.sigma_of(F, p_true)
print('s[:5]:', np.round(s[:5],5))
per = 0.5*(z_ := (y-F)/s)**2 + 0.5*np.log(2*np.pi*s**2) if False else 0
z = (y-F)/s
per = 0.5*z**2 + 0.5*np.log(2*np.pi*s**2)
print('per[:5]:', np.round(per[:5],3))
print('per sum:', round(float(per.sum()),2), ' per min:', round(float(per.min()),2), ' per max:', round(float(per.max()),2))
print('log term[:5]:', np.round(0.5*np.log(2*np.pi*s**2)[:5],4))
print('z2 term max:', round(float((0.5*z**2).max()),3))