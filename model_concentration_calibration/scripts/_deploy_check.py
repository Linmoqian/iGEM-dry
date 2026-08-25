import sys, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'src'))
import numpy as np
import loader, calibrate as cal, forward as fw, deploy, qs_ode

# ---- P2-3: deploy artifact roundtrip (real trigger5 fit) ----
d = loader.load()
f = loader.fold_by_time(d)
m = (f['C'] > 0) & (f['t'] >= 2.0) & (f['t'] <= 9.0) & (f['trigger'] == 5)
p5, z5, fun5 = cal.fit_train(f['C'][m], f['t'][m], f['fold'][m], amp_sign=1.0, seed=5)
art = deploy.build_artifact(p5, t_nodes=(2.0, 3.0, 4.0, 5.0, 6.0, 9.0),
                           meta=dict(trigger=5, source='real-wetlab-2-9h', seed=5))
out = 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/data/processed/calibration_artifact_trigger5.json'
deploy.save_artifact(art, out)
print('artifact saved:', os.path.getsize(out), 'bytes')
keys = list(art['inverse'].keys()); print('LUT nodes:', keys, ' each', len(art['inverse'][keys[0]]['Q']), 'points')
# roundtrip check
errs = []
for ctrue in [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]:
    for tt in [2.0, 3.0, 4.0, 5.0, 6.0, 9.0]:
        q = float(fw.forward_points(np.array([ctrue]), np.array([tt]), p5)[0])
        c_lut = deploy.predict_q2c(art, q, tt)
        c_ana = cal.analytic_inverse(q, tt, p5)
        if c_ana is not None and c_lut is not None:
            errs.append((abs(np.log10(c_lut/ctrue)), abs(np.log10(c_ana/ctrue))))
errs = np.array(errs)
print('LUT roundtrip max log10 err: %.4f, median: %.4f' % (errs[:,0].max(), np.median(errs[:,0])))
print('analytic   max log10 err: %.4f, median: %.4f' % (errs[:,1].max(), np.median(errs[:,1])))

# ---- P2-2: qs_ode prior-sensitivity (prior ranges) ----
print()
print('=== QS-ODE 先验敏感性: 有效 EC50(t=6h) 与幅度 ===')
for Kd in [0.6, 1.5, 3.0]:
    for b in [5.0, 25.0, 60.0]:
        p = dict(qs_ode.DEFAULT); p['Kd_eff'] = Kd; p['b'] = b
        t, Q = qs_ode.simulate([0.0, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0], tmax=1440.0, npts=300, params=p)
        tt = t/60.0
        i6 = int(np.argmin(abs(tt - 6.0)))
        Q6 = Q[:, i6]
        fold6 = Q6 / Q6[0]
        amp = fold6.max() - 1.0
        # effective EC50: C where fold = 1 + amp/2
        target = 1.0 + amp/2
        Cs = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
        ec50 = None
        for j in range(len(Cs)-1):
            if (fold6[j+1] >= target >= fold6[j]) or (fold6[j] >= target >= fold6[j+1]):
                ec50 = float(Cs[j] + (Cs[j+1]-Cs[j])*(target-fold6[j])/(fold6[j+1]-fold6[j]))
                break
        print('Kd_eff=%.1f b=%.0f -> amp(t=6h)=%.3f EC50(t=6h)~%s' % (Kd, b, amp, ('%.2f' % ec50) if ec50 else '>10'))