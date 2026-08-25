import sys, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'src'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import device as dev

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
FIG = os.path.join(BASE, 'figures')

rng = np.random.default_rng(0)
err_nocal, err_cal, err_drift, err_corr = [], [], [], []
for k in range(300):
    a = 1.0 + rng.normal(0, 0.04)
    b = rng.normal(0, 0.004)
    qt = 1.0 + rng.uniform(0.0, 0.5)
    r = dev.readout(np.array([qt]), device_noise=0.02, temp_c=25.0, adc_seed=k, a_gain=a, b_off=b)[0]
    err_nocal.append(abs(r - qt)/qt)
    std_q = np.array([1.0, 1.03, 1.12, 1.38])
    r_std = dev.readout(std_q, device_noise=0.02, temp_c=25.0, adc_seed=k, a_gain=a, b_off=b, n_reps=4).mean(axis=0)
    c = dev.fit_affine(std_q, r_std)
    qhat = dev.apply_affine(r, c)
    err_cal.append(abs(qhat - qt)/qt)
    r2 = dev.readout(np.array([qt]), device_noise=0.02, temp_c=45.0, adc_seed=k, a_gain=a, b_off=b)[0]
    err_drift.append(abs(dev.apply_affine(r2, c) - qt)/qt)
    r3 = dev.readout(np.array([qt]), device_noise=0.02, temp_c=45.0, adc_seed=k, a_gain=a, b_off=b, dark_corrected=True)[0]
    err_corr.append(abs(dev.apply_affine(r3, c) - qt)/qt)
print('median rel err: nocal=%.4f  cal25=%.4f  drift45=%.4f  corr45=%.4f' % (
    np.median(err_nocal), np.median(err_cal), np.median(err_drift), np.median(err_corr)))

plt.figure(figsize=(13.4, 4.3))
ax = plt.subplot(1, 3, 1)
for k, (a, b, seed) in enumerate([(1.02, 0.01, 1), (0.97, -0.008, 2), (1.06, 0.005, 3)]):
    q_true = np.array([1.0, 1.03, 1.12, 1.38])
    r_meas = dev.readout(q_true, device_noise=0.02, temp_c=25.0, adc_seed=seed, a_gain=a, b_off=b, n_reps=4).mean(axis=0)
    c = dev.fit_affine(q_true, r_meas)
    qq = np.linspace(0.95, 1.45, 60)
    ax.plot(qq, c['a']*qq + c['b'], lw=1.4, label='device%d: a=%.3f b=%.4f' % (k+1, c['a'], c['b']))
    ax.scatter(q_true, r_meas, s=26, alpha=0.8)
ax.set_xlabel('Q_true (plate-reader fold)'); ax.set_ylabel('device ratio r')
ax.set_title('(a) 装置仿射标定（4 个标准点）'); ax.legend(fontsize=7.5)
ax = plt.subplot(1, 3, 2)
ax.boxplot([err_nocal, err_cal, err_drift, err_corr],
           tick_labels=['无标定', '25C标定', '漂移+20C\n(未扣暗基线)', '漂移+20C\n(扣暗基线)'],
           showfliers=False, patch_artist=True)
ax.set_ylabel('Q 相对误差'); ax.set_title('(b) 标定/温度漂移/暗基线扣除协议')
ax = plt.subplot(1, 3, 3)
T = np.linspace(-5, 45, 30)
ax.semilogy(T, dev.dark_current(T) * 1e12, color='#d62728', lw=2)
ax.set_xlabel('温度 (C)'); ax.set_ylabel('暗电流 (pA)')
ax.set_title('(c) 暗电流温度漂移 (每+10C 翻倍)')
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig6_device.png'), dpi=165)
plt.close()
print('fig6 v2 ok')