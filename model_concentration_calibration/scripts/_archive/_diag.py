import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42, want_truth=True)
print('Q stats: min', round(float(d['Q'].min()),4), 'max', round(float(d['Q'].max()),4), 'mean', round(float(d['Q'].mean()),4))
import pandas as pd
df = pd.DataFrame(dict(C=d['C'], t=d['t'], Q=d['Q']))
print(df.groupby('t')['Q'].agg(['min','mean','max']).round(3).to_string())
print()
print(df[df['C']==0.0].groupby('t')['Q'].mean().round(3).to_string())
# initial fit quality
z0 = np.array([fw.PRIORS[n][0] for n in fw.PARAM_ORDER])
p0 = fw.inv_transform(z0)
F0 = cal.forward_pts(d['C'], d['t'], p0)
resid = d['Q'] - F0
print('initial residual RMS:', round(float(np.sqrt(np.mean(resid**2))),4), ' mean:', round(float(resid.mean()),4))
print('corrected params:', {k: round(p0[k],3) for k in ['b0','b1','tauB','Amax','tauA','tauD','K0','Kf','tauK','n0','n1','tauN','arel','sfloor']})