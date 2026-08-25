# calibrate.py — v3.1: per-trigger Bayesian calibration on fold-change (amp_sign: +1 / -1)
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import forward as fw


def neg_log_post(z, C, t, y, prior_scale=1.0, amp_sign=1.0):
    p = fw.unpack(fw.inv_transform(z))
    p['Amax'] *= amp_sign
    F = fw.forward_points(C, t, p)
    s = fw.sigma_of(F, p)
    nll = 0.5 * np.sum(((y - F) / s) ** 2 + np.log(2 * np.pi * s ** 2))
    return float(nll - fw.prior_logp(z, scale=prior_scale))


def fit_train(C, t, y, prior_scale=1.0, seed=0, n_restarts=8, amp_sign=1.0):
    z0 = np.array([fw.PRIORS[n][0] for n in fw.PARAM_ORDER])
    rng = np.random.default_rng(seed)
    starts = [z0]
    for _ in range(n_restarts):
        starts.append(z0 + rng.normal(0, 0.6, len(z0)))
    best = None
    for z in starts:
        res = minimize(neg_log_post, z, args=(C, t, y, prior_scale, amp_sign),
                       method='L-BFGS-B', options={'maxiter': 2000, 'ftol': 1e-12})
        if best is None or res.fun < best.fun:
            best = res
    p_hat = fw.unpack(fw.inv_transform(best.x))
    p_hat['Amax'] *= amp_sign
    return p_hat, best.x, float(best.fun)


def laplace_samples(z_hat, C, t, y, prior_scale=1.0, n_samples=1200, seed=1, amp_sign=1.0):
    n = len(z_hat)
    H = np.zeros((n, n))
    eps = 1e-4
    f = lambda z: neg_log_post(z, C, t, y, prior_scale, amp_sign)
    for i in range(n):
        for j in range(n):
            ei = np.zeros(n); ei[i] = eps
            ej = np.zeros(n); ej[j] = eps
            fpp = f(z_hat + ei + ej) - f(z_hat + ei - ej) - f(z_hat - ei + ej) + f(z_hat - ei - ej)
            H[i, j] = fpp / (4 * eps * eps)
    cov = np.linalg.pinv(H)
    cov = (cov + cov.T) / 2
    eigval, eigvec = np.linalg.eigh(cov)
    eigval = np.clip(eigval, 1e-12, None)
    L = eigvec @ np.diag(np.sqrt(eigval))
    rng = np.random.default_rng(seed)
    Z = z_hat[None, :] + rng.normal(0, 1, (n_samples, n)) @ L.T
    draws = np.array([fw.inv_transform(z) for z in Z])
    draws[:, fw.IDX['Amax']] *= amp_sign
    return draws


def logsumexp(a, axis=None):
    amax = np.max(a, axis=axis, keepdims=True)
    return np.log(np.sum(np.exp(a - amax), axis=axis)) + np.squeeze(amax)


def invert_posterior(draws, t_obs, fold_obs, logC_grid=None, c_thr=1.0, c_prior=None):
    """c_prior: (log_mean, log_sd) for a log-normal environmental prior over concentration;
    None = flat in log10C (uninformative)."""
    if logC_grid is None:
        logC_grid = np.linspace(-2.5, 2.0, 231)
    C_grid = 10 ** logC_grid
    n_draws = len(draws)
    loglik = np.zeros((len(C_grid), n_draws))
    for d, p in enumerate(draws):
        F = fw.forward_pts(C_grid, np.array([float(t_obs)]), fw.unpack(p))
        s = fw.sigma_of(F, fw.unpack(p))
        for q in np.atleast_1d(np.asarray(fold_obs, dtype=float)):
            loglik[:, d] += norm.logpdf(q, F[:, 0], s[:, 0])
    logp = logsumexp(loglik, axis=1) - np.log(n_draws)
    if c_prior is not None:
        mu_ln, sd_ln = c_prior
        logp += norm.logpdf(np.log(C_grid), mu_ln, sd_ln)
    logp -= np.max(logp)
    pC = np.exp(logp)
    pC /= np.sum(pC)
    cdf = np.cumsum(pC)
    return dict(mean=float(np.sum(pC * C_grid)),
                median=float(C_grid[np.searchsorted(cdf, 0.5)]),
                lo5=float(C_grid[np.searchsorted(cdf, 0.05)]),
                hi95=float(C_grid[np.searchsorted(cdf, 0.95)]),
                p_ge_1=float(np.sum(pC[C_grid >= c_thr])),
                grid=C_grid, pmf=pC)


def lod_loq(p, t_obs, k_lod=3.0, k_loq=10.0, npts=600):
    C = np.logspace(-2.5, 2.0, npts)
    F = fw.forward_points(C, np.full(npts, float(t_obs)), p)
    s = fw.sigma_of(F, p)
    F0 = float(fw.forward_points([0.0], [float(t_obs)], p)[0])
    s0 = float(fw.sigma_of(np.array([F0]), p)[0])
    def solve(k):
        target = F0 + k * s0
        mask = F >= target
        if not mask.any():
            return None
        idx = int(np.argmax(mask))
        if idx == 0:
            return float(C[0])
        c0, c1 = C[idx - 1], C[idx]
        f0, f1 = F[idx - 1], F[idx]
        return float(c0 + (c1 - c0) * (target - f0) / max(f1 - f0, 1e-12))
    return dict(lod=solve(k_lod), loq=solve(k_loq), blank=F0, blank_sd=s0)


def decision(prob_thr, kappa=10.0):
    thr = 1.0 / (1.0 + kappa)
    return bool(prob_thr > thr), thr


def analytic_inverse(fold, t, p):
    A = p['Amax'] * (1.0 - np.exp(-t / p['tauA'])) * np.exp(-t / p['tauD'])
    K = p['Kf'] + (p['K0'] - p['Kf']) * np.exp(-t / p['tauK'])
    n = p['n0'] + p['n1'] * (1.0 - np.exp(-t / p['tauN']))
    if A <= 0:
        return None
    u = (fold - 1.0) / A
    u = np.clip(u, 1e-9, 1 - 1e-9)
    return K * np.exp(np.log(u / (1 - u)) / n)