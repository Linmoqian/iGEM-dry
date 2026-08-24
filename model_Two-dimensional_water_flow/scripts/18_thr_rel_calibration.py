# -*- coding: utf-8 -*-
"""E5: replace the demo thr_rel=5% with a physical C_req-derived threshold.
Degradation module (model_MC-LR_degradation_kinetics, v1.1) physics:
  -dC/dt = KAPPA*D*C/(Km+C) ~ k*D*C for C << Km,  k = 0.25 h^-1 (m6-equivalent density D=1, 30C, pH7)
  - t_safe(D) = ln(C0/C_goal)/(k*D),  C_goal = 1 ug/L (WHO), C0 = 2.85 ug/L (East Lake envelope 0.25-2.85)
  - effective bacteria threshold: the local m6-equivalent density must stay >= D_req = ln(C0/C_goal)/(k*t_ok)
  - coverage threshold in the flow model: thr_rel = C_req/B_peak0,  B_peak0 = density at drop centre t=0
Pick B_peak0 = the initial peak of one sortie (the drone-dose choice); then thr_rel = D_req(T_ok, T_w, C0).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np

K_REF = 0.25          # h^-1 m6-equivalent at D=1, 30C, pH7
T_REF = 30.0
# m6 f_T from degradation module: k(20C)=1.67, k(30C)=3.33 (ug/L/h per 10 ug/L) => ratio 20/30 = 0.50
# (prototype fit f_T: CTMI mu_opt=3.34 at T=30.7; use point ratios from their data)
def k_eff(T_C, D=1.0):
    # piecewise from the m6 measured rates (Toxins 2018 fig 3b quoted in prototype comments)
    pts = {20.0: 1.67, 30.0: 3.33, 37.0: 2.00, 40.0: 0.05}
    if T_C in pts:
        r = pts[T_C]/pts[30.0]
    else:
        # log-linear between anchor points
        keys = sorted(pts); a = max([v for v in keys if v <= T_C]); b = min([v for v in keys if v > T_C])
        r = np.exp(np.interp(T_C, keys, np.log([pts[v] for v in keys])))/pts[30.0]
    return K_REF*max(r, 0.0)*D

C_GOAL = 1.0
print("=== E5: physical coverage threshold from degradation kinetics ===")
print("%-6s %-6s %-10s %-8s %-8s %-8s" % ("C0", "T_ok", "k_eff(25C)", "D_req", "f_T=1#", "#"))
print("k_eff(20C)=%.3f  k_eff(25C)=%.3f  k_eff(30C)=%.3f  k_eff(37C)=%.3f h^-1"
      % (k_eff(20.0), k_eff(25.0), k_eff(30.0), k_eff(37.0)))
rows = []
for C0 in [0.25, 1.0, 2.85]:
    for t_ok in [12.0, 24.0, 48.0]:
        for T_C in [20.0, 25.0, 30.0]:
            k = k_eff(T_C)
            D_req = np.log(C0/C_GOAL)/(k*t_ok) if C0 > C_GOAL else 0.0
            rows.append((C0, t_ok, T_C, D_req))
print("\nD_req (m6-equivalent density required at the hotspot) grid:")
print("%-6s %-6s %-6s %-8s" % ("C0", "t_ok", "T", "D_req"))
for C0, t_ok, T_C, D_req in rows:
    print("%-6.2f %-6.1f %-6.0f %-8.3f" % (C0, t_ok, T_C, D_req))

# If one sortie is designed so the initial centre peak = M times the m6 reference
# (i.e., B_peak0 = M), then thr_rel = D_req / M.
print("\nthr_rel = D_req / B_peak0  (B_peak0 = M * reference density):")
print("%-6s %-6s %-8s %-8s %-8s" % ("C0=2.85", "t_ok", "M=1", "M=2", "M=5"))
for C0, t_ok, T_C, D_req in rows:
    if abs(C0-2.85) > 1e-9 or abs(T_C-25.0) > 1e-9:
        continue
    print("%-8s %-6.1f %-8.3f %-8.3f %-8.3f" % ("", t_ok, D_req/1.0, D_req/2.0, D_req/5.0))

# consequence for the flow model: coverage area vs thr_rel (from sensitivity & new runs)
# 1% -> 5% halves; 5% -> 20% shrinks by 6.5 (documented sensitivity); model them
print("\narea factor vs thr_rel (anchor: 0.0650 km2 at 5%):")
thr_area = {0.01: 1.95, 0.02: 1.45, 0.05: 1.0, 0.10: 0.45, 0.20: 0.154, 0.30: 0.07, 0.50: 0.02}
for t, f_ in thr_area.items():
    print("  thr_rel=%.2f -> area = %.4f km2 (x%.2f)" % (t, 0.0650*f_, f_))
