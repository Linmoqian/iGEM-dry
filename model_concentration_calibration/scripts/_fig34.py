import sys, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'src'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.metrics import roc_auc_score, roc_curve
import synth, calibrate as cal, forward as fw, device as dev

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
FIG = os.path.join(BASE, 'figures')
d = synth.gen_dataset(seed=42)
ENV = (-1.9, 1.2)

# ---------- FIG3: fit quality ----------
m5 = d['trigger'] == 5
p5, z5, fun5 = cal.fit_train(d['C'][m5], d['t'][m5], d['fold'][m5], amp_sign=1.0)
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))
axes[0].scatter(d['fold'][m5], fw.forward_points(d['C'][m5], d['t'][m5], p5), s=8, alpha=0.5, color='#33507a')
lims = [0.8, 1.9]; axes[0].plot(lims, lims, 'r--', lw=1)
axes[0].set_xlabel('observed fold'); axes[0].set_ylabel('fitted fold')
axes[0].set_title('(a) trigger5 拟合结果 (n=%d, nlp=%.0f)' % (int(m5.sum()), fun5))
for t, col in [(2.0, '#1f77b4'), (4.0, '#2ca02c'), (6.0, '#d62728')]:
    ti = int(np.where(np.isclose(synth.TIMES, t))[0][0])
    Cg = np.logspace(-2.5, 2.0, 120)
    axes[1].plot(Cg, fw.forward_points(Cg, np.full(len(Cg), t), p5), color=col, label=f't={t:g}h')
    sel = m5 & np.isclose(d['t'], t)
    axes[1].scatter(d['C'][sel], d['fold'][sel], s=10, alpha=0.55, color=col, edgecolor='none')
axes[1].set_xscale('log'); axes[1].axvline(1.0, color='red', ls='--', lw=1)
axes[1].set_xlabel('C (ug/L, log)'); axes[1].set_ylabel('Fold')
axes[1].set_title('(b) 拟合曲线与观测点'); axes[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig3_fit.png'), dpi=165); plt.close()
print('fig3 ok')

# ---------- FIG4: multi-time fusion ----------
draws5 = cal.laplace_samples(z5, d['C'][m5], d['t'][m5], d['fold'][m5], n_samples=500, seed=11, amp_sign=1.0)
def postO(pairs, env=ENV, draws=None):
    draws = draws5 if draws is None else draws
    grid = np.linspace(-2.5, 2.0, 231); Cg = 10**grid
    lp = np.zeros(len(Cg))
    for p in draws:
        pt = fw.unpack(p)
        for (tq, qq) in pairs:
            F = fw.forward_points(Cg, np.full(len(Cg), tq), pt)
            s = fw.sigma_of(F, pt)
            lp = lp + norm.logpdf(qq, F, s)
    lp = lp / len(draws) + (norm.logpdf(np.log(Cg), env[0], env[1]) if env else 0)
    lp = lp - lp.max()
    pC = np.exp(lp); pC = pC / pC.sum()
    cdf = np.cumsum(pC)
    return Cg, pC, float(Cg[np.searchsorted(cdf, 0.5)]), float(Cg[np.searchsorted(cdf, 0.05)]), float(Cg[np.searchsorted(cdf, 0.95)]), float(pC[Cg>=1].sum())
def q_at(tid, c, t):
    sel = (d['trigger']==tid) & (d['C']==c) & np.isclose(d['t'], t)
    return float(d['fold'][sel][0])
fig, ax = plt.subplots(figsize=(9.2, 4.6))
cases = [('t=2h', [(2.0, q_at(5,1.0,2.0))], '#1f77b4'),
         ('t=4h', [(4.0, q_at(5,1.0,4.0))], '#2ca02c'),
         ('t=2+4+6h 融合', [(2.0,q_at(5,1.0,2.0)), (4.0,q_at(5,1.0,4.0)), (6.0,q_at(5,1.0,6.0))], '#d62728')]
for lab, pairs, col in cases:
    Cg, pC, md, lo, hi, p1 = postO(pairs)
    ax.plot(Cg, pC, color=col, label='%s: med=%.2f  CI=[%.2f,%.2f]  P(>=1)=%.2f' % (lab, md, lo, hi, p1))
ax.axvline(1.0, color='red', ls='--', lw=1.2)
ax.axvline(0.15, color='grey', ls=':', lw=1.0)
ax.set_xscale('log'); ax.set_xlabel('C (ug/L, log)'); ax.set_ylabel('posterior p(C)')
ax.set_title('多时间点似然融合：真实 C=1 ug/L (trigger5)，后验被逐点拉回真值并收缩')
ax.legend(fontsize=8.5); ax.set_ylim(bottom=0)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig4_fusion.png'), dpi=165); plt.close()
print('fig4 ok')