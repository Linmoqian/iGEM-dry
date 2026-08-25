import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 1
p_hat, z_hat, fun = cal.fit_train(d['C'][m], d['t'][m], d['fold'][m], prior_scale=1.0)
C = np.logspace(-2.5, 2.0, 600)
F = fw.forward_points(C, np.full(600, 6.0), p_hat)
s = fw.sigma_of(F, p_hat)
F0 = float(fw.forward_points([0.0], [6.0], p_hat)[0])
s0 = float(fw.sigma_of(np.array([F0]), p_hat)[0])
print('F0:', F0, 's0:', s0, 'target3:', F0 + 3*s0)
print('F[550:600:10]:', np.round(F[550::10],4))
print('mask.any():', bool((F >= F0+3*s0).any()), 'maxF:', round(float(F.max()),4), 'argmax idx:', int(np.argmax(F)))
ll = cal.lod_loq(p_hat, 6.0)
print('lod_loq:', ll)