import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import loader, numpy as np
d = loader.load()
f = loader.fold_by_time(d)
qc = loader.qc(f)
print('RFP-CV (n, median) per trigger:', {k: (n, round(v,4)) for k,(n,v) in qc.items()})
for tid in [1,5,6,7]:
    m = (f['trigger']==tid) & (f['t']==6.0) & (f['C']>0)
    print(f'trigger{tid} fold@6h median by C:', [round(float(np.nanmedian(f['fold'][m & (f['C']==c)])),3) for c in [0.05,0.1,0.25,0.5,1,2,5]])
# overall fold range per trigger across times
for tid in range(8):
    m = f['trigger']==tid
    print(f'trigger{tid}: fold range [{np.nanmin(f["fold"][m]):.3f}, {np.nanmax(f["fold"][m]):.3f}], n={int(m.sum())}')