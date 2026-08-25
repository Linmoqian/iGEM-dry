# device.py — photodiode readout chain model + per-device affine calibration
import numpy as np

# FPbase / photodiode constants (ref: FPbase sfGFP & TurboRFP; Si photodiode QE)
SENSOR = dict(
    lamb_exc=470.0,  # nm (blue LED excitation)
    sfgfp_ex=485.0, sfgfp_em=510.0, sfgfp_ec=83000.0, sfgfp_qy=0.65,
    turborfp_ex=553.0, turborfp_em=574.0, turborfp_ec=92000.0, turborfp_qy=0.67,
    qe_510=0.78, qe_574=0.72,   # Si photodiode quantum efficiency at emission peaks
    gain=1.0e7,      # transimpedance gain (V/A)
    vref=3.3, adc_bits=12, dark25=62e-12,  # dark current at 25C (A)
    temp_dark_doubling=10.0,  # dark current doubles every +10 C
)


def dark_current(temp_c, p=None):
    p = p or SENSOR
    return p['dark25'] * 2.0 ** ((temp_c - 25.0) / p['temp_dark_doubling'])


def readout(Q_ratio, device_noise=0.05, temp_c=25.0, adc_seed=0, n_reps=1,
            a_gain=1.0, b_off=0.0, led_power=1.0, p=None, dark_corrected=False,
            dark25_frac=0.005):
    # Simplified optical chain (ratio domain): r = a*Q + b + dark(T) + noise
    #   a absorbs LED power, filter/detector efficiency ratio, integration time
    #   dark(T) = dark25_frac * 2^((T-25)/10): dark-current等效偏置，每+10C翻倍
    #     (dark25_frac 为 25C 时暗电流占满量程比例；低光/高TIA增益下可达 0.5%~2%)
    #   dark_corrected=True 模拟每周期先测暗基线(LED关)并扣除，消除温度偏置
    p = p or SENSOR
    rng = np.random.default_rng(adc_seed)
    Q = np.asarray(Q_ratio, dtype=float)
    dark_frac = dark25_frac * 2.0 ** ((temp_c - 25.0) / p['temp_dark_doubling'])
    a = a_gain * led_power
    q_step = p['vref'] / (2 ** p['adc_bits'])
    out = []
    for _ in range(n_reps):
        r_base = a * Q + b_off + (0.0 if dark_corrected else dark_frac)
        noise_rel = device_noise * np.abs(a * Q + b_off) + q_step / np.sqrt(12)
        r = r_base + rng.normal(0, np.abs(noise_rel))
        out.append(r)
    return out[0] if n_reps == 1 else np.array(out)


def fit_affine(Q_ref, r_meas):
    # weighted least squares r = a*Q + b
    Q = np.asarray(Q_ref, dtype=float)
    r = np.asarray(r_meas, dtype=float)
    n = len(Q)
    X = np.vstack([Q, np.ones(n)]).T
    coef, *_ = np.linalg.lstsq(X, r, rcond=None)
    a, b = coef
    resid = r - X @ coef
    s2 = float(np.sum(resid ** 2) / max(n - 2, 1))
    cov = s2 * np.linalg.inv(X.T @ X)
    return dict(a=float(a), b=float(b), cov=cov, resid_sd=float(np.sqrt(s2)))


def apply_affine(r, cal):
    return (r - cal['b']) / cal['a']


def anchor_protocol(Q_true_at_standards, device_noise=0.05, temp_c=25.0, seed=0):
    # standards: 0, 0.5, 1, 5 ug/L measured once each on one device
    r = readout(Q_true_at_standards, device_noise=device_noise, temp_c=temp_c, adc_seed=seed)
    cal = fit_affine(Q_true_at_standards, r)
    return cal