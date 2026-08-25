import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 1
C = d['C'][m]; t = d['t'][m]; y = d['fold'][m]
p = dict(synth.TRIGGER_PROFILES[1]); p['arel']=0.05; p['sfloor']=0.02
F = fw.forward_pts(synth.CONCS, synth.TIMES, p)
print('truth surface t=6 row:', [round(float(v),3) for v in F[:, 6]])
print('data medians t=6 (C=0..10):', [round(float(np.median(y[(C==c) & (np.isclose(t,6))])),3) for c in synth.CONCS])
print('data medians t=2 (C=0..10):', [round(float(np.median(y[(C==c) & (np.isclose(t,2))])),3) for c in synth.CONCS])
print('data medians t=9 (C=0..10):', [round(float(np.median(y[(C==c) & (np.isclose(t,9))])),3) for c in synth.CONCS])
# per batch check at C=10, t=9
mask = (C==10.0) & (np.isclose(t, 9.0))
for b in [0,1,2]:
    mm = mask & (d['batch'][m] == b)
    print(f'batch {b} at C=10,t=9:', [round(float(v),3) for v in y[mm]])