import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, forward as fw
p_true = dict(synth.TRIGGER_PROFILES[1]); p_true['arel']=0.05; p_true['sfloor']=0.02
vals = np.array([p_true[k] for k in fw.PARAM_ORDER])
z = fw.transform(vals)
back = fw.inv_transform(z)
for i, name in enumerate(fw.PARAM_ORDER):
    print(f'{name:6s} val={vals[i]:.4f} z={z[i]:.4f} back={back[i]:.4f} diff={abs(back[i]-vals[i]):.4f}')