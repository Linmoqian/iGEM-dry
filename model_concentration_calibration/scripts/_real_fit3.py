import sys, os, json
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import loader, calibrate as cal, forward as fw
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

d = loader.load()
f = loader.fold_by_time(d)
os.makedirs('D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/data/processed', exist_ok=True)

def fit_window(tmin, tmax, tid, sign, seed=0):
    m = (f['C'] > 0) & (f['t'] >= tmin) & (f['t'] <= tmax) & (f['trigger'] == tid)
    return m, cal.fit_train(f['C'][m], f['t'][m], f['fold'][m], amp_sign=float(sign), seed=seed, n_restarts=6)

out = {}
print('=== window 2-9h (main) ===')
for tid, sign in [(0,1),(1,1),(5,1),(6,1),(2,-1),(7,-1)]:
    m, (p, z, fun) = fit_window(2.0, 9.0, tid, sign, seed=tid)
    rms = float(np.sqrt(np.mean((f['fold'][m] - fw.forward_points(f['C'][m], f['t'][m], p))**2)))
    out[str(tid)] = dict(sign=sign, nlp=fun, rms=rms, params=p)
    print(f'trig{tid}: Amax={p["Amax"]:.3f} K0={p["K0"]:.2f} Kf={p["Kf"]:.2f} tauA={p["tauA"]:.2f} tauD={p["tauD"]:.0f} tauK={p["tauK"]:.2f} n0={p["n0"]:.2f} n1={p["n1"]:.2f} tauN={p["tauN"]:.2f} arel={p["arel"]:.3f} sfloor={p["sfloor"]:.3f} rms={rms:.3f}')
    # detectability z at C=1, t=6
    F1 = float(fw.forward_points(np.array([1.0]), np.array([6.0]), p)[0])
    s1 = float(fw.sigma_of(np.array([F1]), p)[0])
    print(f'    fold(1,6h)={F1:.3f}  sigma={s1:.3f}  z={(F1-1)/s1:.2f}')
print()
print('=== window 2-33h (all) for trigger1/5/6 ===')
for tid, sign in [(1,1),(5,1),(6,1)]:
    m, (p, z, fun) = fit_window(2.0, 33.0, tid, sign, seed=tid+20)
    rms = float(np.sqrt(np.mean((f['fold'][m] - fw.forward_points(f['C'][m], f['t'][m], p))**2)))
    print(f'trig{tid} all-window: Amax={p["Amax"]:.3f} tauA={p["tauA"]:.2f} tauD={p["tauD"]:.1f} K0={p["K0"]:.2f} Kf={p["Kf"]:.2f} rms={rms:.3f}')
    out['trig%d_all' % tid] = dict(sign=sign, nlp=fun, rms=rms, params=p)
json.dump(out, open('D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/data/processed/real_fit_results.json', 'w'), indent=1, default=str)
print('saved json')

# ---- FIG8: real data fits ----
fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.2))
Cg = np.logspace(-2.5, 2.0, 140)
for k, (tid, sign, col) in enumerate([(1,1,'#1f77b4'), (5,1,'#2ca02c'), (6,1,'#d62728'), (7,-1,'#9467bd')]):
    m, (p, z, fun) = fit_window(2.0, 9.0, tid, sign, seed=tid)
    axes[0].plot(Cg, fw.forward_points(Cg, np.full(len(Cg), 6.0), p), color=col, lw=1.8, label=f'trigger{tid} (Amax={p["Amax"]:+.2f})')
    sel = m & np.isclose(f['t'], 6.0)
    axes[0].scatter(f['C'][sel], f['fold'][sel], s=22, alpha=0.5, color=col)
axes[0].axvline(1.0, color='red', ls='--', lw=1.1)
axes[0].set_xscale('log'); axes[0].set_ylim(0.55, 1.75)
axes[0].set_xlabel('C (ug/L, log)'); axes[0].set_ylabel('Fold @ t=6h')
axes[0].set_title('(a) 真实湿实验数据 t=6h 观测点与拟合 (2-9h窗口)'); axes[0].legend(fontsize=7.5)
for k, (tid, col) in enumerate([(1,'#1f77b4'),(5,'#2ca02c')]):
    m, (p, z, fun) = fit_window(2.0, 9.0, tid, 1, seed=tid)
    for tt, mk in [(3.0,'o'), (6.0,'s'), (9.0,'^')]:
        sel = (f['C']>0) & (f['t']==tt) & (f['trigger']==tid)
        med = [float(np.median(f['fold'][sel & (f['C']==c)])) for c in [0.05,0.1,0.25,0.5,1,2,5]]
        axes[1].plot([0.05,0.1,0.25,0.5,1,2,5], med, mk+'-', color=col, ms=4, alpha=0.6, lw=1.0)
        axes[1].plot([0.05,0.1,0.25,0.5,1,2,5], fw.forward_points(np.array([0.05,0.1,0.25,0.5,1,2,5]), np.full(7, tt), p), mk+'--', color=col, ms=4, lw=1.0, alpha=0.9)
axes[1].set_xscale('log'); axes[1].axvline(1.0, color='red', ls='--', lw=1.1)
axes[1].set_xlabel('C (ug/L, log)'); axes[1].set_ylabel('Fold')
axes[1].set_title('(b) trigger1/5 中位观测(实线) vs 模型(虚线), t=3/6/9h')
zs = []; labs = []
for tid, sign in [(0,1),(1,1),(5,1),(6,1)]:
    m, (p, z, fun) = fit_window(2.0, 9.0, tid, sign, seed=tid)
    F1 = float(fw.forward_points(np.array([1.0]), np.array([6.0]), p)[0])
    s1 = float(fw.sigma_of(np.array([F1]), p)[0])
    zs.append((F1-1.0)/s1); labs.append(f'trig{tid}')
axes[2].bar(labs, zs, color=['#1f77b4','#2ca02c','#d62728','#9467bd'][:4])
axes[2].axhline(3.0, color='orange', ls='--', lw=1.2, label='3-sigma 单点检出基准')
axes[2].set_ylabel('z = (fold(1ug/L,6h)-1)/sigma'); axes[2].set_title('(c) 1 ug/L 单点可检性 (z 分数)')
axes[2].legend(fontsize=7.5); axes[2].set_ylim(0, max(zs)+1)
plt.tight_layout()
plt.savefig('D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/figures/fig8_realdata_fit.png', dpi=165)
plt.close()
print('fig8 ok')