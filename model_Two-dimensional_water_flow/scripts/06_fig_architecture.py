# -*- coding: utf-8 -*-
"""Architecture diagram (matplotlib) for MODEL_ARCHITECTURE.md"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

fm.fontManager.addfont("C:/Windows/Fonts/simhei.ttf")
plt.rcParams["font.family"] = "SimHei"
plt.rcParams["axes.unicode_minus"] = False

FIG = os.path.join(os.path.dirname(__file__), "..", "figures")
fig, ax = plt.subplots(figsize=(15.5, 9.2))
ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis("off")

def box(x, y, w, h, text, fc="#e8f1fb", ec="#2b6cb0", fs=10.0, lw=1.4):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=2))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs, zorder=3, color="#1a365d")

def arrow(x1, y1, x2, y2, text="", color="#2b6cb0", fs=9):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5), zorder=1)
    if text:
        ax.text((x1+x2)/2, (y1+y2)/2+0.7, text, ha="center", fontsize=fs, color="#c53030", zorder=4)

box(2, 50, 21, 7, """① 监测输入
漂浮检测节点(MC-LR/位置)
+ 风场(Open-Meteo 2023-24)
+ Open-Meteo统计(年均2.87m/s, N扇区26.6%)""",
    "#fef3c7", "#d69e2e", fs=9.5)
box(26, 50, 18, 7, """② 风险斑块生成
ML水质模型(model_redo_v2)
/ IDW空间插值
→ bloom patch (椭圆/栅格)""",
    "#fed7d7", "#c53030", fs=9.5)
box(47, 50, 17, 7, """③ 湖盆与数据
OSM边界 31.2 km2
重构水深 (均2.21m/最大4.64m)
HydroLAKES / DEM / MIKE21参数""",
    "#e6fffa", "#2c7a7b", fs=9.5)
box(67, 50, 14, 7, """④ 无人机参数
航速/航程/投放精度
σ0=25 m/载荷/悬停""",
    "#e2e8f0", "#4a5568", fs=9.5)
box(84, 50, 14, 7, """⑤ 降解动力学
C_req (有效菌浓度)
threshold接口 (5%)""",
    "#e2e8f0", "#4a5568", fs=9.5)

box(14, 28, 30, 15, """【流场层】2D 浅水方程 (半隐式, dt=20 s, 50 m网格)
d(eta)/dt + div(H*u) = 0
d(u)/dt = -g*grad(eta) + f*cross(u) + tau_w/(rho*H)
          - (g*n^2*|u|*u)/H^(4/3) + nu*lap(u)
风应力 Cd=1.3e-3(可Wu型) | Coriolis f=7.4e-5 | Manning n=0.0238
Smagorinsky Cs=0.28 | 源/汇开边界(±Q)可选
→ 稳态风生环流 (u, v, η), 质量守恒<1e-15(η方程积分)""",
    "#ebf8ff", "#3182ce", fs=9.2)

box(48, 28, 26, 15, """【输运层】Lagrangian 粒子
RK4 平流 + 随机游走 (D=0.3 m²/s) + 岸线反射
批量并行: k个候选点 × N粒子 同时积分
→ 浓度场 C(x,t) (直方图+高斯核)
→ 覆盖率 cov(t) = ∫[C ≥ thr_rel·C_peak] dA
→ 漂移椭圆主轴/质心/逃逸率""",
    "#faf5ff", "#805ad5", fs=9.2)

box(78, 28, 20, 15, """【决策层】投放点优化
J(p) = Σ_w p(w)·|cov(p,w)∩bloom|/|bloom|
5成员风况系综 (2.0-3.0 m/s, 120-150°)
候选网格 200 m
→ Top-K 投放点
+ 期望覆盖分数场 + 重投放触发""",
    "#fff5f5", "#e53e3e", fs=9.2)

box(6, 6, 44, 14, """【输出 / 后处理】
· 单次覆盖面积-时间曲线 (多阈值曲族)
· 最优投放点 + 预期覆盖地图
· 不确定性区间 (系综分位数)
· 敏感性 (风速/方向/Manning/阈值/σ0)
· 与 MIKE21东湖/文献量级对照报告""",
    "#f0fff4", "#276749", fs=9.5)

box(56, 6, 42, 14, """【验证层】
· 驻波解析周期 (误差 0.16%)
· 体积守恒 (<1e-15)
· 矩形盆风生环流解析平衡 (η坡降对齐理论)
· 动量平衡分解 / dt收敛性 (10/20/40 s)
· 结论: 模型可靠, 输出进入决策流程""",
    "#fffff0", "#b7791f", fs=9.5)

arrow(12, 50, 25, 43)
arrow(35, 50, 32, 43)
arrow(55, 50, 57, 43)
arrow(74, 50, 66, 43)
arrow(92.5, 50, 90, 43)
arrow(29, 28, 44, 28, "流场 (u, v, η)")
arrow(44, 35.5, 48, 35.5, "粒子/浓度场")
arrow(74, 35.5, 78, 35.5, "覆盖指标")
arrow(15, 20, 15, 6)
arrow(56, 20, 62, 20, "验证结论回流")
arrow(78, 20, 78, 6)
plt.tight_layout()
fig.savefig(os.path.join(FIG, "fig00_architecture.png"), dpi=140)
print("saved fig00")
