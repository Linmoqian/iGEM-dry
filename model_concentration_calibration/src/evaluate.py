# evaluate.py — leave-one-batch-out CV + metrics
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
import calibrate as cal


def metrics_from_inversions(y_true, inv, thr_prior=None):
    y = np.asarray(y_true, dtype=float)
    med = np.array([i['median'] for i in inv])
    mean = np.array([i['mean'] for i in inv])
    lo = np.array([i['lo5'] for i in inv])
    hi = np.array([i['hi95'] for i in inv])
    p1 = np.array([i['p_ge_1'] for i in inv])
    pos = y > 0
    logerr = np.log10(np.clip(med[pos] / y[pos], 1e-6, 1e6))
    mael = float(np.mean(np.abs(logerr)))
    rmsle = float(np.sqrt(np.mean(logerr ** 2)))
    bias = float(np.mean(logerr))
    cover = float(np.mean((y >= lo) & (y <= hi)))
    label = (y >= 1.0).astype(int)
    auc = float(roc_auc_score(label, p1)) if len(np.unique(label)) > 1 else float('nan')
    fpr, tpr, thr = roc_curve(label, p1) if len(np.unique(label)) > 1 else (None, None, None)
    return dict(mae_log10=mael, rmsle=rmsle, bias_log10=bias, coverage90=cover,
                auc_threshold=auc, p_ge_1=p1, y=y, fpr=fpr, tpr=tpr, thresholds=thr)


def lobo_cv(data, prior_scale=1.0, n_samples=400, seed=7, verbose=True):
    # data contract: keys C/t/fold/batch (synth.gen_dataset); legacy 'Q' alias accepted
    if 'fold' not in data and 'Q' in data:
        data['fold'] = data['Q']
    batches = np.unique(data['batch'])
    all_inv = []
    for b in batches:
        m = data['batch'] != b
        p_hat, z_hat, fun = cal.fit_train(data['C'][m], data['t'][m], data['Q'][m], prior_scale=prior_scale)
        draws = cal.laplace_samples(z_hat, data['C'][m], data['t'][m], data['Q'][m],
                                    prior_scale=prior_scale, n_samples=n_samples, seed=seed + int(b))
        sel = data['batch'] == b
        # subsample rows for speed (cap 120 points)
        idx = np.where(sel)[0]
        if len(idx) > 120:
            idx = idx[:: int(np.ceil(len(idx) / 120))]
        for i in idx:
            inv = cal.invert_posterior(draws, data['t'][i], data['Q'][i])
            all_inv.append(dict(y=float(data['C'][i]), med=inv['median'], mean=inv['mean'],
                                lo=inv['lo5'], hi=inv['hi95'], p1=inv['p_ge_1']))
    return all_inv


def summarize(inv_list):
    y = np.array([i['y'] for i in inv_list])
    med = np.array([i['med'] for i in inv_list])
    lo = np.array([i['lo'] for i in inv_list])
    hi = np.array([i['hi'] for i in inv_list])
    p1 = np.array([i['p1'] for i in inv_list])
    pos = y > 0
    logerr = np.log10(np.clip(med[pos] / y[pos], 1e-6, 1e6))
    label = (y >= 1.0).astype(int)
    auc = float(roc_auc_score(label, p1)) if len(np.unique(label)) > 1 else float('nan')
    return dict(n=len(inv_list),
                mae_log10=float(np.mean(np.abs(logerr))),
                rmsle=float(np.sqrt(np.mean(logerr ** 2))),
                bias_log10=float(np.mean(logerr)),
                coverage90=float(np.mean((y >= lo) & (y <= hi))),
                auc=auc)