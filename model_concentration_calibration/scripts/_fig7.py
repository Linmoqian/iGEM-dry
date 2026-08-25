import sys, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'src'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import synth, calibrate as cal, forward as fw

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
FIG = os.path.join(BASE, 'figures')
d = synth.gen_dataset(seed=42)

# ---------- FIG7: trigger comparison + LOD table ----------
fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.2))
colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd']
lods = {}
for k, (tid, sign) in enumerate([(1,1),(5,1),(6,1),(7,-1)]):
    m = d['trigger'] == tid
    p_h, z_h, f_h = cal.fit_train(d['C'][m], d['t'][m], d['fold'][m], amp_sign=sign)
    Cg = np.logspace(-2.5, 2.0, 160)
    F = fw.forward_points(Cg, np.full(len(Cg), 6.0), p_h)
    axes[0].plot(Cg, F, color=colors[k], lw=1.8, label='trigger%d (amp=%+.2f)' % (tid, p_h['Amax']))
    if sign > 0:
        ll = cal.lod_loq(p_h, 6.0)
        lods[tid] = ll['lod']
axes[0].axvline(1.0, color='red', ls='--', lw=1.1)
axes[0].set_xscale('log'); axes[0].set_ylim(0.82, 1.75)
axes[0].set_xlabel('C (ug/L, log)'); axes[0].set_ylabel('Fold @ t=6h')
axes[0].set_title('(a) 四类 trigger 构型的响应形状 (t=6h)'); axes[0].legend(fontsize=8)
aucs = {}
for tid, sign in [(1,1),(5,1),(6,1)]:
    p1s, ys = [], []
    m = d['trigger'] == tid
    for b in [0,1,2]:
        tr = m & (d['batch'] != b); te = m & (d['batch'] == b)
        p_h, z_h, f_h = cal.fit_train(d['C'][tr], d['t'][tr], d['fold'][tr], amp_sign=sign)
        dr = cal.laplace_samples(z_h, d['C'][tr], d['t'][tr], d['fold'][tr], n_samples=150, seed=29+b, amp_sign=sign)
        sel = te & (d['t'] == 6.0)
        for i in np.where(sel)[0]:
            inv = cal.invert_posterior(dr, 6.0, float(d['fold'][i]), c_prior=(-1.9, 1.2))
            p1s.append(inv['p_ge_1']); ys.append(float(d['C'][i]))
    from sklearn.metrics import roc_auc_score
    aucs[tid] = roc_auc_score((np.array(ys)>=1).astype(int), p1s)
    print('trigger', tid, 'AUC', round(aucs[tid],3), 'n', len(ys))
axes[1].bar([str(k) for k in aucs.keys()], list(aucs.values()), color=['#1f77b4','#2ca02c','#d62728'])
axes[1].set_ylim(0.6, 1.0)
axes[1].set_ylabel('1ug/L 预警 AUC (LOBO)')
axes[1].set_title('(b) 预警判别力对比')
for k, v in aucs.items(): axes[1].text(str(k), v + 0.01, '%.3f' % v, ha='center', fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig7_triggers.png'), dpi=165); plt.close()
print('fig7 ok')
print('LOD@t=6h per trigger:', {k: round(v,3) for k,v in lods.items()})