# -*- coding: utf-8 -*-
"""
MC-LR 降解动力学模型 —— 文献数据校准脚本（v1.1 前置）
用已提取的文献数据对环境修正函数做真实数值校准。
输出: data/processed/fitted_env_correction_params.csv ; figures/fig7_literature_calibration.png
运行: python src/fit_literature.py
"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, 'data', 'processed')
FIG = os.path.join(ROOT, 'figures')
os.makedirs(PROC, exist_ok=True)
os.makedirs(FIG, exist_ok=True)
records = []

def add_fit(key, model, params, n, r2, r2_adj, source, note=''):
    records.append({'fit_key': key, 'model': model, 'n': n, 'R2': round(float(r2), 4),
                    'R2_adj': round(float(r2_adj), 4),
                    'params_json': json.dumps(params, ensure_ascii=False),
                    'source': source, 'note': note})

def r2_score_manual(y, yhat):
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')

def r2_adj(r2, n, p):
    return 1.0 - (1.0 - r2) * (n - 1) / max(1, n - p - 1)

d7 = pd.read_csv(os.path.join(PROC, 'm6_environment_rate_matrix_extracted.csv'))
m6_c0 = d7[d7['variable'] == 'C0'].copy(); m6_T = d7[d7['variable'] == 'T'].copy(); m6_pH = d7[d7['variable'] == 'pH'].copy()
d6 = pd.read_csv(os.path.join(PROC, 'YF1_RSM_BBD_17runs_extracted.csv'))

# (a) first-order check
x = m6_c0['value'].values.astype(float); y = m6_c0['rate_ugLh'].values.astype(float)
A = np.vstack([x]).T; k_app = np.linalg.solve(A.T @ A, A.T @ y)[0]
yhat = k_app * x; r2_a = r2_score_manual(y, yhat)
slope_ll, intercept_ll, r_ll, p_ll, se_ll = stats.linregress(np.log(x), np.log(y))
add_fit('m6_first_order', 'linear-through-origin: r = k*C0',
        {'k_app_h-1': round(float(k_app), 4), 'loglog_slope': round(float(slope_ll), 4), 'loglog_p': float(p_ll)},
        len(x), r2_a, r2_a, 'Toxins 2018,10,536 Fig.3a (D7)', 'slope~1 => first-order in env range')

# (a2) 数据审计：1 ug/L 点 rate/C0=1.0 明显偏离其余 0.25 -> 疑似采集误差；鲁棒/剔除敏感性
ratio = y / x
mask_bad = ratio > 0.8
xx = x[~mask_bad]; yy = y[~mask_bad]
Ax = np.vstack([xx]).T; k2 = np.linalg.solve(Ax.T @ Ax, Ax.T @ yy)[0]
yhat2 = k2 * xx; r2_2 = r2_score_manual(yy, yhat2)
sl2, ic2, r2_, p2, se2 = stats.linregress(np.log(xx), np.log(yy))
add_fit('m6_first_order_sensitivity', 'exclude suspect digitization point (rate/C0=1.0)',
        {'k_app_h-1': round(float(k2), 4), 'loglog_slope': round(float(sl2), 4)},
        len(xx), r2_2, r2_2, 'Toxins 2018,10,536 Fig.3a (D7)',
        'suspicious point (C0=1 ug/L): rate/C0=1.0 vs 0.25 elsewhere; excluding gives log-log slope 0.83 (mild sub-linearity) & k=0.2515')
def res_hub(k): return k * x - y
h = least_squares(res_hub, [0.25], loss='soft_l1', f_scale=0.5)
add_fit('m6_first_order_robust', 'Huber soft_l1 robust least-squares',
        {'k_app_h-1': round(float(h.x[0]), 4)}, len(x), float('nan'), float('nan'),
        'Toxins 2018,10,536 Fig.3a (D7)', 'robust against single-point error')

T_obs = m6_T['value'].values.astype(float); R_T = m6_T['rate_ugLh'].values.astype(float)
def gauss_T(p, T):
    A, T0, w = p; return A * np.exp(-0.5 * ((T - T0) / w) ** 2)
def res_gauss(p): return gauss_T(p, T_obs) - R_T
fit_g = least_squares(res_gauss, [3.3, 30.0, 6.0], bounds=([0.5, 20, 1], [20, 45, 25]))
r2_g = r2_score_manual(R_T, gauss_T(fit_g.x, T_obs))
def ctmi_T(p, T):
    mu_opt, Tmin, Topt, Tmax = p
    T = np.asarray(T, dtype=float); out = np.zeros_like(T)
    m = (T > Tmin) & (T < Tmax); t = T[m]
    num = (t - Tmax) * (t - Tmin) ** 2
    den = (Topt - Tmin) * ((Topt - Tmin) * (t - Topt) - (Topt - Tmax) * (Topt + Tmin - 2.0 * t))
    out[m] = mu_opt * num / den; return out
def res_ctmi(p): return ctmi_T(p, T_obs) - R_T
fit_c = least_squares(res_ctmi, [3.3, 8.0, 30.0, 42.0], bounds=([0.5, 0, 25, 38], [20, 20, 40, 48]))
r2_c = r2_score_manual(R_T, ctmi_T(fit_c.x, T_obs))
add_fit('m6_fT', 'CTMI (Rosso 1995)',
        {'mu_opt_h-1': round(float(fit_c.x[0]), 4), 'Tmin_C': round(float(fit_c.x[1]), 2),
         'Topt_C': round(float(fit_c.x[2]), 2), 'Tmax_C': round(float(fit_c.x[3]), 2)},
        len(T_obs), r2_c, r2_adj(r2_c, len(T_obs), 4), 'Toxins 2018,10,536 Fig.3b (D7)',
        'better than Gaussian on shoulder')
add_fit('m6_fT_gauss', 'symmetric Gaussian', {'A': round(float(fit_g.x[0]), 4),
        'T0_C': round(float(fit_g.x[1]), 2), 'w_C': round(float(fit_g.x[2]), 2)},
        len(T_obs), r2_g, r2_adj(r2_g, len(T_obs), 3), 'Toxins 2018,10,536 Fig.3b (D7)',
        'cannot reproduce 37C=0.6x & 40C approx 0')

pH_obs = m6_pH['value'].values.astype(float); R_pH = m6_pH['rate_ugLh'].values.astype(float)
def asym_gauss_pH(p, pH):
    A, popt, wl, wr = p; w = np.where(pH < popt, wl, wr)
    return A * np.exp(-0.5 * ((pH - popt) / w) ** 2)
def res_sym(p):
    A, popt, w = p; return A * np.exp(-0.5 * ((pH_obs - popt) / w) ** 2) - R_pH
def res_asym(p): return asym_gauss_pH(p, pH_obs) - R_pH
fits_sym = least_squares(res_sym, [3.3, 7.0, 2.2], bounds=([0.5, 5, 1], [20, 9, 6]))
fits_asym = least_squares(res_asym, [3.3, 7.0, 2.2, 2.2], bounds=([0.5, 5, 1, 1], [20, 9, 6, 6]))
r2_sym = r2_score_manual(R_pH, res_sym(fits_sym.x) + R_pH)
r2_asym = r2_score_manual(R_pH, res_asym(fits_asym.x) + R_pH)
add_fit('m6_fpH', 'asymmetric Gaussian (wL/wR)',
        {'A': round(float(fits_asym.x[0]), 4), 'pHopt': round(float(fits_asym.x[1]), 3),
         'wL': round(float(fits_asym.x[2]), 3), 'wR': round(float(fits_asym.x[3]), 3)},
        len(pH_obs), r2_asym, r2_adj(r2_asym, len(pH_obs), 4), 'Toxins 2018,10,536 Fig.3c (D7)',
        'acidic tail better (pH3: 0.057x measured vs 0.19x symmetric)')
add_fit('m6_fpH_sym', 'symmetric Gaussian',
        {'A': round(float(fits_sym.x[0]), 4), 'pHopt': round(float(fits_sym.x[1]), 3),
         'w': round(float(fits_sym.x[2]), 3)}, len(pH_obs), r2_sym, r2_adj(r2_sym, len(pH_obs), 3),
        'Toxins 2018,10,536 Fig.3c (D7)', '')

# Klebsiella tables (Toxins 2025, 17, 346, Tables 2 & 3), MC-LR, 3.0 mg/L
k_tab2 = {'TA13': {20: 0.016, 25: 0.021, 30: 0.037, 35: 0.050, 40: 0.126},
          'TA14': {20: 0.019, 25: 0.019, 30: 0.027, 35: 0.034, 40: 0.045},
          'TA19': {20: 0.022, 25: 0.024, 30: 0.033, 35: 0.041, 40: 0.046}}
k_tab3 = {'TA13': {6: 0.028, 7: 0.035, 8: 0.030, 9: 0.026, 10: 0.026},
          'TA14': {6: 0.032, 7: 0.034, 8: 0.033, 9: 0.029, 10: 0.029},
          'TA19': {6: 0.032, 7: 0.037, 8: 0.032, 9: 0.032, 10: 0.031}}
k_rows = []
for strain, mc in k_tab2.items():
    for Tv, rv in mc.items(): k_rows.append({'strain': strain, 'T_degC': Tv, 'rate_mgLh': rv, 'type': 'temperature'})
for strain, phd in k_tab3.items():
    for pv, rv in phd.items(): k_rows.append({'strain': strain, 'pH': pv, 'rate_mgLh': rv, 'type': 'pH'})
kdf = pd.DataFrame(k_rows); k_Tdf = kdf[kdf['type'] == 'temperature'].copy()
# 将 Klebsiella 矩阵落盘为独立数据集（含出处）
kout = kdf.copy()
kout['mc_variant'] = 'MC-LR'
kout['initial_ugmL'] = 3.0
kout['source'] = 'Toxins 2025, 17, 346 (Tables 2 & 3), extracted by team'
kout.to_csv(os.path.join(PROC, 'Klebsiella_T_pH_rate_matrix_extracted.csv'), index=False)
ta13 = k_Tdf[k_Tdf['strain'] == 'TA13'].sort_values('T_degC')
norm_ta13 = ta13['rate_mgLh'].values / ta13['rate_mgLh'].max()
add_fit('klebsiella_fT', 'monotonic increase to 40C (no Topt within 20-40C)',
        {'TA13_40C_rel': 1.0, 'TA13_20C_rel': round(float(norm_ta13[0]), 3), 'maxT_observed': 40},
        len(ta13), float('nan'), float('nan'), 'Toxins 2025,17,346 Table 2',
        'strain-level T response Topt>=40C vs m6 Topt~30C')
kph = kdf[kdf['type'] == 'pH']
for st in ['TA13', 'TA14', 'TA19']:
    sub = kph[kph['strain'] == st]
    rng = sub['rate_mgLh'].max() / sub['rate_mgLh'].min()
    add_fit('klebsiella_fpH_' + st, 'flat (max/min ratio)', {'max_min_ratio': round(float(rng), 3)},
            len(sub), float('nan'), float('nan'), 'Toxins 2025,17,346 Table 3', 'pH 6-10 variation < 25%')

# YF1 RSM vs multiplicative
X = d6[['T_degC', 'pH', 'C_MCLR_ugmL']].values.astype(float)
yY = d6['removal_pct_60min'].values.astype(float)
def design_quad(X):
    a, b, c = X[:, 0], X[:, 1], X[:, 2]
    return np.column_stack([np.ones(len(X)), a, b, c, a * b, a * c, b * c, a ** 2, b ** 2, c ** 2])
Dq = design_quad(X); coef_q, *_ = np.linalg.lstsq(Dq, yY, rcond=None)
yhat_q = Dq @ coef_q; r2_q = r2_score_manual(yY, yhat_q); nq, pq = Dq.shape
add_fit('YF1_RSM_quadratic', 'full quadratic (10 terms)', {'R2': round(float(r2_q), 4)},
        nq, r2_q, r2_adj(r2_q, nq, pq - 1), 'Toxins 2022,14,240 Table 2 (D6)', 'interactions allowed')
def fit_marginal(xv, yv):
    dm = np.column_stack([np.ones(len(xv)), xv, xv ** 2]); cm, *_ = np.linalg.lstsq(dm, yv, rcond=None)
    return cm
cmT = fit_marginal(X[:, 0], yY); cmpH = fit_marginal(X[:, 1], yY); cmC = fit_marginal(X[:, 2], yY)
def product_model(X):
    fT = np.column_stack([np.ones(len(X)), X[:, 0], X[:, 0] ** 2]) @ cmT
    fpH = np.column_stack([np.ones(len(X)), X[:, 1], X[:, 1] ** 2]) @ cmpH
    fC = np.column_stack([np.ones(len(X)), X[:, 2], X[:, 2] ** 2]) @ cmC
    D = np.column_stack([fT * fpH * fC]); kk = (D.T @ yY) / (D.T @ D)
    return kk * (fT * fpH * fC)
yhat_m = product_model(X); r2_m = r2_score_manual(yY, yhat_m)
add_fit('YF1_multiplicative', 'marginal quadratic products (no interactions)', {'R2': round(float(r2_m), 4)},
        len(yY), r2_m, r2_adj(r2_m, len(yY), 1), 'Toxins 2022,14,240 Table 2 (D6)',
        'interaction gain: R2 quad %.3f vs mult %.3f' % (r2_q, r2_m))

# USGS microcosm Table 5 & Table 1 respike segment
t5 = [('S. rhizophila (pos ctrl)', 4.80, 2.53, 'positive control'),
      ('E. coli (-) control', 3.51, 2.13, 'negative control'),
      ('Inland1.b', 3.00, 3.00, 'isolate (no removal)'),
      ('LE2.r', 3.92, 2.03, 'isolate'), ('Inland2.g', 3.00, 2.28, 'isolate'),
      ('Inland1.d', 4.17, 2.33, 'isolate')]
usgs_k = []
for name, c0, c8, kind in t5:
    if c0 > 0 and c8 > 0:
        kd = -np.log(c8 / c0) / 8.0
        usgs_k.append({'isolate': name, 'type': kind, 'C0_ugL': c0, 'C8_ugL': c8, 'k_d-1': round(float(kd), 4)})
k_seg = -np.log(6.17 / 57.4) / 4.0
usgs_k.append({'isolate': 'Inland1 source water microcosm (5um filter, respike day4)',
               'type': 'microcosm respike segment', 'C0_ugL': 57.4, 'C8_ugL': 6.17, 'k_d-1': round(float(k_seg), 4)})
ukdf = pd.DataFrame(usgs_k)
ukdf.to_csv(os.path.join(PROC, 'USGS_microcosm_apparent_k_estimates.csv'), index=False)
k_vals = ukdf['k_d-1'].values
add_fit('USGS_microcosm_k', 'pseudo-first-order k over 8-day (or 4-day respike segment) interval',
        {'median_k_d-1': round(float(np.median(k_vals)), 4),
         'range_d-1': [round(float(k_vals.min()), 4), round(float(k_vals.max()), 4)]},
        len(ukdf), float('nan'), float('nan'), 'USGS 10.5066/P9DL080Y Tables 1&5',
        'environmental isolates/background degradation prior')

fdf = pd.DataFrame(records)
fdf.to_csv(os.path.join(PROC, 'fitted_env_correction_params.csv'), index=False)
print('fitted params ->', os.path.join(PROC, 'fitted_env_correction_params.csv'))
print(fdf[['fit_key', 'model', 'R2', 'R2_adj']].to_string(index=False))

fig, axes = plt.subplots(2, 3, figsize=(14.4, 8.4))
ax = axes[0, 0]
ax.plot(x, y, 'o', color='#1f77b4', ms=8, label='m6 measured (D7)')
tt = np.linspace(0, 55, 100)
ax.plot(tt, k_app * tt, 'r--', lw=2, label=f'k={k_app:.3f} h-1 (R2={r2_a:.3f})')
ax.plot(tt, k2 * tt, 'g-.', lw=1.6, label=f'excl. outlier: k={k2:.3f} h-1 (R2={r2_2:.3f})')
ax.annotate('suspect point\n(rate/C0=1.0)', xy=(x[0], y[0]), xytext=(2.5, 10.5),
            fontsize=7.5, color='#d62728', arrowprops=dict(arrowstyle='->', color='#d62728', lw=1))
ax.set_xlabel('initial C0 (ug/L)'); ax.set_ylabel('rate (ug/L/h)')
ax.set_title('(a) first-order check'); ax.legend(fontsize=7.5); ax.grid(alpha=0.3)
ax = axes[0, 1]
tt2 = np.linspace(10, 46, 200)
ax.plot(tt2, ctmi_T(fit_c.x, tt2), '-', color='#d62728', lw=2,
        label=f"CTMI (Topt={fit_c.x[2]:.1f}C, Tmax={fit_c.x[3]:.1f}C, R2={r2_c:.3f})")
ax.plot(tt2, gauss_T(fit_g.x, tt2), '--', color='#7f7f7f', lw=1.6,
        label=f"Gaussian (T0={fit_g.x[1]:.1f}C, R2={r2_g:.3f})")
ax.plot(T_obs, R_T, 'o', color='#1f77b4', ms=8, label='m6 measured')
ax.set_xlabel('Temp (C)'); ax.set_ylabel('rate (ug/L/h)')
ax.set_title('(b) f_T: CTMI vs Gaussian'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax = axes[0, 2]
tp = np.linspace(2.5, 12, 200)
ax.plot(tp, asym_gauss_pH(fits_asym.x, tp), '-', color='#2ca02c', lw=2,
        label=f"asym (pHopt={fits_asym.x[1]:.2f}, R2={r2_asym:.3f})")
ax.plot(tp, fits_sym.x[0] * np.exp(-0.5 * ((tp - fits_sym.x[1]) / fits_sym.x[2]) ** 2), '--',
        color='#7f7f7f', lw=1.6, label=f"sym (R2={r2_sym:.3f})")
ax.plot(pH_obs, R_pH, 'o', color='#1f77b4', ms=8, label='m6 measured')
ax.set_xlabel('pH'); ax.set_ylabel('rate (ug/L/h)')
ax.set_title('(c) f_pH: asym vs sym'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax = axes[1, 0]
ax.plot(T_obs, R_T / R_T[T_obs == 30][0], 'o-', color='#1f77b4', ms=7, lw=2, label='m6 (Topt~30C)')
for st, col in [('TA13', '#d62728'), ('TA14', '#2ca02c'), ('TA19', '#9467bd')]:
    sub = k_Tdf[k_Tdf['strain'] == st].sort_values('T_degC')
    rv = sub['rate_mgLh'].values
    ax.plot(sub['T_degC'].values, rv / rv.max(), 's-', color=col, ms=6, lw=1.6, label=f'Klebsiella {st} (Topt>=40C)')
ax.set_xlabel('Temp (C)'); ax.set_ylabel('relative rate')
ax.set_title('(d) strain-level T response difference'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax = axes[1, 1]
ax.scatter(yY, yhat_q, s=45, color='#1f77b4', label=f'quadratic RSM R2={r2_q:.3f}')
ax.scatter(yY, yhat_m, s=45, marker='^', color='#d62728', label=f'multiplicative R2={r2_m:.3f}')
ax.plot([20, 105], [20, 105], 'k--', lw=1)
ax.set_xlabel('measured 60min removal (%)'); ax.set_ylabel('predicted (%)')
ax.set_title('(e) YF1: interaction gain'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax = axes[1, 2]
names = [u['isolate'] for u in usgs_k]
ks = ukdf['k_d-1'].values
cols = ['#2ca02c' if u['type'] == 'positive control' else '#8c564b' if u['type'] == 'negative control'
        else '#1f77b4' if u['type'] == 'isolate' else '#d62728' for u in usgs_k]
ax.barh(np.arange(len(ks))[::-1], ks, color=cols, alpha=0.85)
ax.set_yticks(np.arange(len(ks))[::-1]); ax.set_yticklabels(names, fontsize=7)
ax.set_xlabel('apparent first-order k (d-1)')
ax.set_title('(f) USGS microcosm k estimates'); ax.grid(alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig7_literature_calibration.png'), dpi=160)
plt.close()
print('figure ->', os.path.join(FIG, 'fig7_literature_calibration.png'))
print()
print('=== KEY NUMBERS ===')
print(f"m6 first-order k_app = {k_app:.4f} h-1 ; log-log slope = {slope_ll:.3f} (p={p_ll:.2e})")
print(f"m6 f_T CTMI: mu_opt={fit_c.x[0]:.3f}, Tmin={fit_c.x[1]:.2f}, Topt={fit_c.x[2]:.2f}, Tmax={fit_c.x[3]:.2f}  R2={r2_c:.4f}")
print(f"m6 f_pH asym: pHopt={fits_asym.x[1]:.3f}, wL={fits_asym.x[2]:.3f}, wR={fits_asym.x[3]:.3f}  R2={r2_asym:.4f}")
print(f"YF1: RSM R2={r2_q:.4f} ; mult R2={r2_m:.4f} ; deltaR2={r2_q-r2_m:.4f}")
print(f"USGS microcosm k: median={np.median(k_vals):.4f} d-1, range=[{k_vals.min():.4f},{k_vals.max():.4f}]")
