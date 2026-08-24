# -*- coding: utf-8 -*-
"""Redraw fig02 with visible quiver arrows."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.viz import setup_style
import matplotlib.pyplot as plt
ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
setup_style()
labels = ["SE_2p5", "N_3p0", "W_2p0"]
fig, axes = plt.subplots(1, 3, figsize=(19, 5.2))
for ax, lab in zip(axes, labels):
    f = dict(np.load(os.path.join(PROC, "flow_%s.npz" % lab)))
    uc, vc, mask, xs, ys = f["uc"], f["vc"], f["mask"], f["xs"], f["ys"]
    sp = np.sqrt(uc**2 + vc**2)
    im = ax.pcolormesh(xs, ys, sp, cmap="viridis", shading="auto")
    x2, y2 = np.meshgrid(xs, ys)
    step = 5
    ax.quiver(x2[::step, ::step], y2[::step, ::step], uc[::step, ::step], vc[::step, ::step],
              color="w", width=0.0022, scale=0.9, headwidth=3.2, headlength=4)
    ax.set_title("%s: %.1f m/s from %.0f deg | max=%.3f m/s" % (lab, f["wind_mps"], f["wind_dir"], float(sp[mask].max())))
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
fig.colorbar(im, ax=axes, shrink=0.85, label="speed (m/s)")
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig02_circulation_3scenarios.png"), dpi=130)
print("fig02 redrawn")
