import sys, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'src'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.metrics import roc_auc_score, roc_curve
import synth, calibrate as cal, forward as fw

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
FIG = os.path.join(BASE, 'figures')
os.makedirs(FIG, exist_ok=True)
d = synth.gen_dataset(seed=42)
ENV = (-1.9, 1.2)
CS = synth.CONCS; TS = synth.TIMES

# ===== FIG2: mechanistic family (trigger1) ===== 
fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.0))
F1 = synth.surface(1)
im = axes[0].imshow(F1, aspect='auto', origin='lower', cmap='viridis',
                    extent=[TS[0], TS[-1], np.log10(CS[1]), np.log10(CS[-1])])
axes[0].set_xlabel('time t (h)'); axes[0].set_ylabel('log10 C (ug/L)')
axes[0].set_title('(a) 折合比曲面 F(C,t) — trigger1')
fig.colorbar(im, ax=axes[0], label='Fold')
for c, col in [(0.25, '#1f77b4'), (0.5, '#2ca02c'), (1.0, '#d62728'), (2.0, '#9467bd'), (5.0, '#8c564b')]:
    F = synth.surface(1)
    axes[1].plot(TS, F[int(np.where(CS == c)[0][0])], '-o', ms=3, color=col, label=f'{c} ug/L')
axes[1].axhline(1.0, color='grey', lw=0.8, ls='--')
axes[1].set_xlabel('time t (h)'); axes[1].set_ylabel('Fold Q(C,t)/Q0(t)')
axes[1].set_title('(b) 时间响应族'); axes[1].legend(fontsize=8)
for t, col in [(2.0, '#1f77b4'), (4.0, '#2ca02c'), (6.0, '#d62728')]:
    ti = int(np.where(np.isclose(TS, t))[0][0])
    axes[2].plot(CS, F1[:, ti], '-o', ms=3, color=col, label=f't={t:g}h')
axes[2].set_xscale('log'); axes[2].axvline(1.0, color='red', ls='--', lw=1.0)
axes[2].set_xlabel('C (ug/L, log)'); axes[2].set_ylabel('Fold')
axes[2].set_title('(c) 剂量-响应曲线族'); axes[2].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig2_family.png'), dpi=165); plt.close()
print('fig2 ok')