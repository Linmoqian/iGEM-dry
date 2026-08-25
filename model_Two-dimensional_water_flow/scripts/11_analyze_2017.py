import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import numpy as np
from swflow.viz import setup_style
import matplotlib.pyplot as plt
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PROC = os.path.join(ROOT, 'data', 'processed')
FIG = os.path.join(ROOT, 'figures')
setup_style()
d = np.load(os.path.join(PROC, 'flow_2017period_hourly.npz'), allow_pickle=True)
t = list(d['t']); umax = np.array(d['umax']); umean = np.array(d['umean']); spd = np.array(d['spd'])
print('n hours:', len(umax), 'umax mean %.3f std %.3f range [%.3f, %.3f]' % (umax.mean(), umax.std(), umax.min(), umax.max()))
print('umean mean %.4f std %.4f' % (umean.mean(), umean.std()))
# 6-hourly fields
uc = d['uc']; vc = d['vc']
print('snapshots:', len(uc), 'shape', uc[0].shape)
U = np.stack([np.sqrt(uc[k]**2+vc[k]**2) for k in range(len(uc))])
Umean = U.mean(axis=0)
Ustd = U.std(axis=0)
print('std of speed field about its mean: mean %.4f max %.4f' % (float(Ustd[Ustd>0].mean()), float(Ustd.max())))
# successive 6h change
diffs = [float(np.sqrt(np.mean((U[k+1]-U[k])**2))) for k in range(len(U)-1)]
print('successive 6h RMS change: mean %.4f max %.4f' % (np.mean(diffs), np.max(diffs)))
print('relative to peak speed %.3f: %.1f%%/6h' % (float(Umean.max()), 100.0*np.mean(diffs)/float(Umean.max())))
# wind time series figure
fig, axes = plt.subplots(2, 1, figsize=(13, 6.5), sharex=True)
axes[0].plot(range(len(spd)), spd, lw=0.8, label='wind speed (m/s)')
axes[0].plot(range(len(umax)), umax, lw=1.4, label='flow |u|max')
axes[0].legend(); axes[0].set_ylabel('m/s')
axes[0].set_title('2017-11-15 -- 2017-12-17 time-varying wind & lake flow (MIKE21 paper period)')
axes[1].plot(range(len(umean)), umean, lw=1.2, color='tab:green')
axes[1].set_ylabel('flow |u|mean')
import numpy as _np
idx = [i for i, tt in enumerate(t) if i % 24 == 0]
axes[1].set_xticks(idx)
axes[1].set_xticklabels([t[i][5:10] for i in idx], rotation=45, fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(FIG, 'fig06_2017period.png'), dpi=130)
print('saved fig06')