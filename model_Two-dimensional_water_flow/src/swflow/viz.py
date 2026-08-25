# -*- coding: utf-8 -*-
"""
swflow.viz - shared plotting config (CJK font) and helpers.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

def setup_style():
    for f in ['C:/Windows/Fonts/simhei.ttf', 'C:/Windows/Fonts/msyh.ttc']:
        if os.path.exists(f):
            fm.fontManager.addfont(f)
    plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 110
    plt.rcParams['savefig.dpi'] = 130

def cell_velocities(state):
    """cell-centered u,v from staggered faces (for interpolation & plotting)"""
    u = state['u']; v = state['v']
    uc = 0.5*(u[:, :-1] + u[:, 1:])
    vc = 0.5*(v[:-1, :] + v[1:, :])
    return uc, vc
