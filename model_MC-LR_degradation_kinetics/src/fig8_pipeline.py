# -*- coding: utf-8 -*-
# fig8: 降解模型作为五模块管线中'反应核服务'的接口图
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for _f in ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC']:
    try:
        font_manager.findfont(_f, fallback_to_default=False)
        matplotlib.rcParams['font.sans-serif'] = [_f, 'DejaVu Sans']
        break
    except Exception:
        continue
matplotlib.rcParams['axes.unicode_minus'] = False
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, 'figures')
os.makedirs(FIG, exist_ok=True)

fig, ax = plt.subplots(figsize=(13.4, 7.0))
ax.set_xlim(0, 13.4); ax.set_ylim(0, 7.0); ax.axis('off')

def box(x, y, w, h, text, fc, ec, fs=8.2):
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.06', fc=fc, ec=ec, lw=1.4)
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs)

def arrow(x1, y1, x2, y2, label='', color='#333', fs=7.0, ls='-'):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=13, lw=1.3, color=color, linestyle=ls)
    ax.add_patch(a)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.16, label, fontsize=fs, ha='center', color=color)

ax.text(6.7, 6.75, 'MC-LR 降解动力学模型 —— 五模块管线中的「反应核服务」（v1.3 目标接口）',
        ha='center', fontsize=12, fontweight='bold')

# 时间轴
ax.text(0.3, 6.30, '时间尺度层级： 标高定/redo_v2 小时级(nowcast)   |   降解 小时-天   |   水流 36h 自旋/0.25-3h 输运   |   路径 秒-分钟', fontsize=7.8, color='#555')

# 上游（左侧两盒）
box(0.25, 4.55, 3.1, 1.45, '上游 A：浓度标定模型\n(荧光比值->浓度)\n输出: median/lo5/hi95\nP(C>=1ug/L), 质量旗标\n(LOD 0.28-1.34 ug/L, 小时级, 已除装置仿射)', '#fff6e5', '#c98a2b')
box(0.25, 2.85, 3.1, 1.45, '上游 B：total MC/MC-LR 预测\n(CMADRE v2, nowcast)\n输出: median/q10/q90,\np_detected/p_exceedance/ood\n(无东湖毒素标签, 域外程度)', '#fff6e5', '#c98a2b')

# 中心：降解模型
box(4.0, 2.85, 4.3, 3.15, '降解模型（v1.2 数字换锚后）\n\n内核（不动）：\n机理 ODE 级联 C->L->P->X\n+ B(t) 菌群 / E(t) 诱导 (Hill)\n+ 环境修正 CTMI f_T / 非对称 f_pH\n+ 层次贝叶斯 (株间 T_opt_j, k_j)\n+ 机会约束反问题\n\n接口层（v1.3 新增）：\n[1] scenario(c0+sigma | redo分布+ood)\n[2] kernel.sink_rate(C,B,T,pH,t)\n[3] kernel.dose_response(C0,env,T_limit,alpha)\n[4] kernel.t_safe_quantiles(...)\n[5] kernel.C_req(菌密度阈值)  <-> thr_rel\n[6] online_update(复测读数)', '#e8f6ea', '#2e8b57', fs=7.9)

# 下游
box(8.9, 4.55, 4.2, 1.45, '横向：二维浅水流 (东湖 31.2 km2, 50m grid)\n输出: 流场 u,v / sim_drop:\narea_km2(单次覆盖), centroid, theta\nTop-K 候选 + 风况系综 member_scores\n覆盖定义 coverage={C>=thr_rel*C_peak}\n>>> 反馈给降解: k_dil(x,t), tau_mix, T_drift', '#eef2fd', '#4a6ac0')
box(8.9, 2.85, 4.2, 1.45, '下游：任务级路径规划 (MD-MUAV-VRPTWP-E)\n消费(来自降解模型的 degradation_json):\ndue_min <- t_safe(D_max) 分位\nlag.degrade_min {median,p90}\ndemand <- dosage_ugL/cells_L 换算\n返回: 每风险点到达时刻 T_arrive\n投递包数 / 架次时间表', '#f7eefb', '#8b4ac0')

# 反馈
box(8.9, 1.05, 4.2, 1.45, '闭环反馈：检测节点治理后复测\n-> 浓度标定模型 (C_post +/- CI)\n-> [6] 在线贝叶斯更新 (k 后验漂移)\n-> 归档为治理案例用于 v1.2 校准\n(注: 标定 LOD 0.28-1.34 ug/L 需覆盖\n  东湖低浓度 0.25-0.43 ug/L 验证带)', '#fdf3e3', '#c98a2b')

arrow(3.35, 5.27, 4.0, 5.27, 'C0~N(mu,sigma^2)+环境先验', color='#c98a2b')
arrow(3.35, 3.57, 4.0, 3.90, '触发+预测场景 C0 (ood 阈值)', color='#c98a2b')
arrow(8.3, 5.27, 8.9, 5.27, 'C_req <-> thr_rel; sink_rate 供粒子属性', color='#4a6ac0')
arrow(8.3, 3.57, 8.9, 3.57, 'degradation_json; t_safe 分位', color='#8b4ac0')
arrow(8.9, 3.57, 8.3, 3.80, 'T_arrive; 投放包数', color='#8b4ac0', ls='--')
arrow(8.9, 2.85, 8.3, 2.85, '', color='#8b4ac0', ls='--')
arrow(11.0, 2.85, 11.0, 1.55, '治理后复测', color='#c98a2b', ls='--')

ax.text(6.7, 0.55, '注：v1.2 先完成数字换锚（QA 报告 A1-A4）：m6 k=0.25 h-1 为采样网格伪影；速率先验改 CQ5/Ho2012/伊利湖/USGS/Mendeley 分层；CTMI/f_pH 降为形状假设。\n管线联调（v1.3）基于换锚后的参数；新增数据（Mendeley 时间序列 / Lake Erie 变体全谱 / 东湖 2009 水华）直接支撑 k_bg、f_intra、f_LR、C0 场景库四项先验。', ha='center', fontsize=7.4, color='#555')

plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig8_pipeline_interfaces.png'), dpi=160)
plt.close()
print('saved')