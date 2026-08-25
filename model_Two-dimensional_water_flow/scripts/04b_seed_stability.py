import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import numpy as np
from swflow.deployment import batch_sim_drops, bloom_patch
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PROC = os.path.join(ROOT, 'data', 'processed')
labels = ['m0', 'SE_2p5', 'm1', 'm2', 'm3']
flows = [dict(np.load(os.path.join(PROC, 'flow_%s.npz' % lab))) for lab in labels]
flow0 = flows[1]
xs, ys, dx = flow0['xs'], flow0['ys'], float(flow0['dx'])
mask = flow0['mask']
patch = bloom_patch(mask, xs, ys, cx=-1300.0, cy=-200.0, rx=900.0, ry=500.0, theta_deg=20.0)
jj, ii = np.where(mask)
sel = (ii % 4 == 0) & (jj % 4 == 0)
cands = np.column_stack([(xs[ii[sel]]), (ys[jj[sel]])])
for seed in [1, 2]:
    scores = []
    for f in flows:
        outs = batch_sim_drops(f, cands, T_h=1.5, dt=10.0, D=0.3, n=600, sigma0=25.0, thr_rel=0.05, rng_seed=seed)
        s = [float((cov & patch).sum())/max(1.0, float(patch.sum())) for (area, cxy, C, cov) in outs]
        scores.append(np.array(s))
    S = np.mean(scores, axis=0)
    order = np.argsort(-S)
    top = [tuple(np.round(cands[k], 0)) for k in order[:5]]
    print('seed', seed, 'top5:', top)
    print('  scores:', np.round(S[order[:5]], 4))