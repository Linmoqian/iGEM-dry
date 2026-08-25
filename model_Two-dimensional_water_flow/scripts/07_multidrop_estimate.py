# -*- coding: utf-8 -*-
import numpy as np, os
PROC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'processed')
d = np.load(os.path.join(PROC, 'opt_result.npz'))
cands, S = d['cands'], d['scores']
order = np.argsort(-S)
# greedy spaced selection (min distance 600 m)
chosen = []
for k in order:
    p = cands[k]
    if all(np.hypot(p[0]-q[0], p[1]-q[1]) >= 600.0 for q in chosen):
        chosen.append(p)
    if len(chosen) >= 8:
        break
print('chosen (spaced 600m):')
for p in chosen:
    idx = np.where((cands[:,0]==p[0]) & (cands[:,1]==p[1]))[0][0]
    print('  (%.0f, %.0f)  S=%.3f' % (p[0], p[1], S[idx]))
# cumulative upper bound (sum of fractions, overlap ignored -> upper bound)
idx = [np.where((cands[:,0]==p[0]) & (cands[:,1]==p[1]))[0][0] for p in chosen]
cum = np.cumsum(S[idx])
print('cumulative expected fraction (upper bound):', np.round(cum, 3))
print('patch area 1.41 km2; best single: %.1f%%' % (100*S[idx[0]]))
