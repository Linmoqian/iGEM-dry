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
d = synth.gen_dataset(seed=42)
ENV = (-1.9, 1.2)

# ---------- FIG5: LOD/decision; ROC; reliability ----------
m5 = d['trigger'] == 5
p5, z5, fun5 = cal.fit_train(d['C'][m5], d['t'][m5], d['fold'][m5], amp_sign=1.0)
draws5 = cal.laplace_samples(z5, d['C'][m5], d['t'][m5], d['fold'][m5], n_samples=400, seed=11)
Cg = np.logspace(-2.5, 2.0, 160)
Fmed = np.median(np.array([fw.forward_points(Cg, np.full(len(Cg), 6.0), fw.unpack(p)) for p in draws5]), axis=0)
Flo = np.percentile(np.array([fw.forward_points(Cg, np.full(len(Cg), 6.0), fw.unpack(p)) for p in draws5]), 5, axis=0)
Fhi = np.percentile(np.array([fw.forward_points(Cg, np.full(len(Cg), 6.0), fw.unpack(p)) for p in draws5]), 95, axis=0)
ll = cal.lod_loq(p5, 6.0)
fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.1))
axes[0].fill_between(Cg, Flo, Fhi, color='#33507a', alpha=0.18, label='90% 参数后验带')
axes[0].plot(Cg, Fmed, color='#33507a', lw=1.8, label='后验中位曲线')
axes[0].axhline(ll['blank'] + 3*ll['blank_sd'], color='orange', ls='--', lw=1.1, label='3-sigma 空白阈值 (LOD)')
axes[0].axhline(ll['blank'] + 10*ll['blank_sd'], color='purple', ls='--', lw=1.1, label='10-sigma (LOQ, 本案例不可达)')
if ll['lod'] is not None:
    axes[0].axvline(ll['lod'], color='orange', ls=':', lw=1.2)
    axes[0].annotate('LOD=%.2f ug/L' % ll['lod'], xy=(ll['lod'], 1.62), fontsize=8.5, color='orange', ha='center')
axes[0].axvline(1.0, color='red', ls='--', lw=1.1)
axes[0].set_xscale('log'); axes[0].set_ylim(0.95, 1.72)
axes[0].set_xlabel('C (ug/L, log)'); axes[0].set_ylabel('Fold @ t=6h')
axes[0].set_title('(a) 剂量响应 + LOD/LOQ (trigger5)'); axes[0].legend(fontsize=7.6)
p1s, ys = [], []
for tid, sign in [(1,1),(5,1),(6,1)]:
    m = d['trigger'] == tid
    for b in [0,1,2]:
        tr = m & (d['batch'] != b); te = m & (d['batch'] == b)
        p_h, z_h, f_h = cal.fit_train(d['C'][tr], d['t'][tr], d['fold'][tr], amp_sign=sign)
        dr = cal.laplace_samples(z_h, d['C'][tr], d['t'][tr], d['fold'][tr], n_samples=200, seed=19+b, amp_sign=sign)
        sel = te & (d['t'] == 6.0)
        for i in np.where(sel)[0]:
            inv = cal.invert_posterior(dr, 6.0, float(d['fold'][i]), c_prior=ENV)
            p1s.append(inv['p_ge_1']); ys.append(float(d['C'][i]))
p1s = np.array(p1s); ys = np.array(ys)
lab = (ys >= 1.0).astype(int)
fpr, tpr, thrs = roc_curve(lab, p1s)
auc = roc_auc_score(lab, p1s)
axes[1].plot(fpr, tpr, color='#33507a', lw=2, label='P(C>=1) 阈值判定, AUC=%.3f' % auc)
axes[1].plot([0,1],[0,1], '--', color='grey', lw=1)
axes[1].set_xlabel('false positive rate'); axes[1].set_ylabel('true positive rate')
axes[1].set_title('(b) 1 ug/L 预警 ROC (LOBO CV)'); axes[1].legend(fontsize=8.5)
bins = np.linspace(0, 1, 7)
cent, freq = [], []
for i in range(len(bins)-1):
    sel = (p1s >= bins[i]) & (p1s < bins[i+1])
    if sel.sum() >= 5:
        cent.append((bins[i]+bins[i+1])/2); freq.append(float(lab[sel].mean()))
axes[2].plot(cent, freq, 'o-', color='#d62728', label='观测频率')
axes[2].plot([0,1],[0,1], '--', color='grey', lw=1, label='完美校准')
axes[2].set_xlabel('预测概率 bin 中心'); axes[2].set_ylabel('观测频率')
axes[2].set_title('(c) 可靠性图 (LOBO)'); axes[2].legend(fontsize=8.5)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig5_lod_decision.png'), dpi=165); plt.close()
print('fig5 ok  AUC=%.3f  n=%d' % (auc, len(p1s)))