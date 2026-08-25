import sys
sys.path.insert(0, 'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/src')
import numpy as np
from scipy.stats import norm
import synth, calibrate as cal, forward as fw
d = synth.gen_dataset(seed=42)
m = d['trigger'] == 5
p_hat, z_hat, fun = cal.fit_train(d['C'][m], d['t'][m], d['fold'][m], amp_sign=1.0)
draws = cal.laplace_samples(z_hat, d['C'][m], d['t'][m], d['fold'][m], n_samples=500, seed=9)
def posterior_obs(pairs, env=(-1.9, 1.2)):
    grid = np.linspace(-2.5, 2.0, 231); Cg = 10**grid
    lp = np.zeros(len(Cg))
    for p in draws:
        pt = fw.unpack(p)
        for (tq, qq) in pairs:
            F = fw.forward_points(Cg, np.full(len(Cg), tq), pt)
            s = fw.sigma_of(F, pt)
            lp = lp + norm.logpdf(qq, F, s)
    lp = lp / len(draws) + norm.logpdf(np.log(Cg), env[0], env[1])
    lp = lp - lp.max()
    pC = np.exp(lp); pC = pC / pC.sum()
    cdf = np.cumsum(pC)
    return dict(C=Cg, p=pC, median=float(Cg[np.searchsorted(cdf, 0.5)]),
                lo5=float(Cg[np.searchsorted(cdf, 0.05)]), hi95=float(Cg[np.searchsorted(cdf, 0.95)]),
                p1=float(pC[Cg>=1].sum()))
sel4 = m & (d['C']==1.0) & (d['t']==4.0); q4 = float(d['fold'][sel4][0])
sel6 = m & (d['C']==1.0) & (d['t']==6.0); q6 = float(d['fold'][sel6][0])
a = posterior_obs([(4.0, q4)])
b = posterior_obs([(2.0, float(d['fold'][m & (d['C']==1.0) & (d['t']==2.0)][0]))])
c = posterior_obs([(2.0, float(d['fold'][m & (d['C']==1.0) & (d['t']==2.0)][0])), (4.0, q4), (6.0, q6)])
print('t=2h only : median', round(b['median'],3), 'CI', round(b['lo5'],3), round(b['hi95'],3), 'P>=1', round(b['p1'],3))
print('t=4h only : median', round(a['median'],3), 'CI', round(a['lo5'],3), round(a['hi95'],3), 'P>=1', round(a['p1'],3))
print('fusion 2+4+6: median', round(c['median'],3), 'CI', round(c['lo5'],3), round(c['hi95'],3), 'P>=1', round(c['p1'],3))