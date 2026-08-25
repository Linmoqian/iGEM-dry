import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import forward as fw
import synth
F = synth.surface(1)
print('F shape:', F.shape, 'max:', round(float(F.max()), 3), 'min:', round(float(F.min()), 3))
p = dict(synth.TRIGGER_PROFILES[1]); p['arel']=0.05; p['sfloor']=0.02
F2 = fw.forward_pts(synth.CONCS, synth.TIMES, p)
print('F2 max check:', round(float(F2.max()),3))
print('F2 C=10 row:', [round(float(v),3) for v in F2[-1]])