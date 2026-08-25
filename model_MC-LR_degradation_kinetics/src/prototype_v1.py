# -*- coding: utf-8 -*-
"""
MC-LR 降解动力学模型 —— 原型 v1（示意图与架构验证用）
用途：为《模型架构设计报告》生成图表，验证“机理 ODE + 环境修正 + 不确定性”架构的可运行性。
说明：参数为文献校准的示意值（见代码内注释与报告中参数表），正式版本需湿实验数据校准。
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

# 中文字体（注意：图中会用到 CJK 字符）
for _f in ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC']:
    try:
        font_manager.findfont(_f, fallback_to_default=False)
        matplotlib.rcParams['font.sans-serif'] = [_f, 'DejaVu Sans']
        break
    except Exception:
        continue
matplotlib.rcParams['axes.unicode_minus'] = False
from scipy.integrate import solve_ivp

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures')
os.makedirs(FIG_DIR, exist_ok=True)
np.random.seed(42)

# ---------------------------------------------------------------- 参数（文献校准示意值）
# 参考: Sphingopyxis sp. m6 (10.3390/toxins10120536) 在 1-50 ug/L 环境浓度下近似一级 k=0.25 h^-1 (30C, pH7)
#       MlrA 粗酶伪一级 k 最高 9.36 h^-1 (10.3390/microorganisms9081594)；CQ5 一级 k=0.01537 h^-1 (10.1007/s13213-019-01510-6)
K_APP_REF = 0.25          # h^-1，基准伪一级速率常数（m6 当量菌密度 D=1、30C、pH7）
KM = 100.0                # ug/L，饱和常数（示意：环境浓度范围内远小于 Km，行为近似一级）
KAPPA = K_APP_REF * KM    # kcat*E 归一化系数，使 C<<Km 时 -dC/dt = K_APP_REF*C

# 温度修正（m6: 20C=1.67, 30C=3.33, 37C=2.00, 40C≈0 ug/L/h @10 ug/L）
T_REF = 30.0
def f_T(T):
    T = np.asarray(T, dtype=float)
    # 双常数指数型贝塞尔曲线近似（峰值 30C）
    return np.exp(-0.5 * ((T - T_REF) / 7.0) ** 2) * (T < 38.0)

# pH 修正（m6: pH3=0.19, 5=1.48, 7=3.33, 9=1.67, 11=0.52 ug/L/h @10ug/L, 30C）
PH_REF = 7.0
def f_pH(pH):
    pH = np.asarray(pH, dtype=float)
    return np.exp(-0.5 * ((pH - PH_REF) / 2.2) ** 2)

def degradation_rate(C, B_ratio, T, pH):
    """单位体积总降解速率 (ug/L/h)。B_ratio: 菌密度相对 m6 当量 (7e9 CFU/mL) 的倍数。"""
    return KAPPA * B_ratio / (KM + C) * C * f_T(T) * f_pH(pH)

def decay_model(t, y, B0, T, pH, delta=0.10, k2=0.05):
    """两状态模型：C=环状MC-LR(ug/L), L=线性化MC-LR(ug/L)。B(t)=B0*exp(-delta*t)（光控自杀/环境死亡）。"""
    C, L = y
    B = B0 * np.exp(-delta * t)
    r1 = KAPPA * B / (KM + C) * f_T(T) * f_pH(pH) * C        # MlrA 环开环
    r2 = k2 * B * f_T(T) * f_pH(pH) * L                        # 简化：后续断裂（MlrB/C）合并为一级
    return [-r1, r1 - r2]

def solve(C0, B0, T=30.0, pH=7.0, t_end=48.0, delta=0.10):
    sol = solve_ivp(decay_model, [0, t_end], [C0, 0.0], args=(B0, T, pH, delta),
                    method='LSODA', dense_output=True, rtol=1e-7, atol=1e-9, max_step=0.25)
    t = np.linspace(0, t_end, 481)
    y = sol.sol(t)
    return t, y

def time_to_safety(C0, B0, T=30.0, pH=7.0, C_target=1.0, delta=0.10, t_max=96.0):
    t, y = solve(C0, B0, T, pH, t_max, delta)
    idx = np.where(y[0] <= C_target)[0]
    return t[idx[0]] if len(idx) else np.nan

# ================================================================ 图3：文献动力学数据重构
def fig3_literature():
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.6))
    # (a) m6: 速率 vs C0 (线性, k~0.25 h-1)
    ax = axes[0, 0]
    c0 = np.array([1, 10, 20, 30, 40, 50.0])
    r = np.array([1.0, 3.33, 5.0, 7.5, 10.0, 12.5])
    ax.plot(c0, r, 'o-', color='#1f77b4', lw=2)
    ax.plot(c0, 0.25 * c0, '--', color='gray', label='k = 0.25 h^¹ (一级)')
    ax.set_xlabel('初始 MC-LR 浓度 (μg/L)'); ax.set_ylabel('降解速率 (μg/L/h)')
    ax.set_title('(a) m6 速率 vs 初始浓度 (30℃, pH7)\n近似一级：k≈0.25 h^¹')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    # (b) m6: 速率 vs T
    ax = axes[0, 1]
    Ts = np.array([20, 30, 37, 40.0]); rs = np.array([1.67, 3.33, 2.0, 0.0])
    tt = np.linspace(15, 42, 100)
    ax.plot(tt, 3.33 * f_T(tt), '-', color='#d62728', lw=2, label='模型 f_T(T)')
    ax.plot(Ts, rs, 'o', color='#d62728', ms=7, label='m6 实测')
    ax.set_xlabel('温度 (℃)'); ax.set_ylabel('降解速率 (μg/L/h)')
    ax.set_title('(b) 温度修正 f_T(T)（钟形，最适 30℃）')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    # (c) m6: 速率 vs pH
    ax = axes[0, 2]
    pHs = np.array([3, 5, 7, 9, 11.0]); rp = np.array([0.19, 1.48, 3.33, 1.67, 0.52])
    pp = np.linspace(3, 12, 100)
    ax.plot(pp, 3.33 * f_pH(pp), '-', color='#2ca02c', lw=2, label='模型 f_pH(pH)')
    ax.plot(pHs, rp, 'o', color='#2ca02c', ms=7, label='m6 实测')
    ax.set_xlabel('pH'); ax.set_ylabel('降解速率 (μg/L/h)')
    ax.set_title('(c) pH 修正 f_pH(pH)（钟形，最适 pH7）')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    # (d) CQ5 一级拟合
    ax = axes[1, 0]
    t = np.linspace(0, 244, 200)
    S = 14.12 * np.exp(-0.01537 * t)
    ax.plot(t, S, '-', color='#9467bd', lw=2, label='lnS=2.64764−0.01537t')
    ax.axhline(1.0, color='red', ls='--', lw=1, label='WHO 阈值 1 μg/L')
    ax.set_xlabel('时间 (h)'); ax.set_ylabel('MC-LR (μg/L)')
    ax.set_title('(d) CQ5: 一级动力学 k=0.01537 h^¹\n(14.12→1.57 μg/L, 244 h, 88.9%)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.set_ylim(0, 15)
    # (e) 各体系速率常数量级对比
    ax = axes[1, 1]
    names = ['CQ5\n全细胞', 'Kansole&Lin\nBacillus(mlr-)', 'MlrA+杀菌滤液\n共处理(7d, 94.2%)',
             'm6 全细胞\n(环境浓度)', 'Lake Erie\n原位菌群', '沙滤生物膜\n(MC类, 下限)', 'MlrA 粗酶\n(重组E.coli)']
    ks = [0.01537, 0.0167, 0.017, 0.25, 0.375, 1.8, 9.36]
    colors = ['#9467bd', '#e377c2', '#8c564b', '#1f77b4', '#17becf', '#7f7f7f', '#ff7f0e']
    ypos = np.arange(len(ks))
    ax.barh(ypos, ks, color=colors, alpha=0.85)
    ax.set_yticks(ypos); ax.set_yticklabels(names, fontsize=8)
    ax.set_xscale('log'); ax.set_xlabel('伪一级速率常数 k (h^¹, log)')
    ax.set_title('(e) 文献速率常数量级对比（跨体系差异 >3 个数量级）')
    ax.grid(alpha=0.3, axis='x')
    # (f) MlrA+杀菌滤液共处理剂量效应（Microorganisms 2021, 9, 1594 第7天数据）
    ax = axes[1, 2]
    vals = [79.11, 94.2]
    ax.bar(['5% (v/v) 滤液', '10% (v/v) 滤液'], vals, color=['#8c564b', '#d62728'], alpha=0.85)
    ax.set_ylabel('第 7 天 MCs 去除率 (%)'); ax.set_ylim(0, 105)
    ax.set_title('(f) 共处理体系剂量-去除率（第 7 天）')
    for i, v in enumerate(vals):
        ax.text(i, v + 1.5, f'{v:.1f}%', ha='center', fontsize=8)
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig3_literature_kinetics.png'), dpi=160)
    plt.close()

# ================================================================ 图4：不同剂量下的降解轨迹
def fig4_trajectories():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
    ax = axes[0]
    for B0, c, ls in [(0.5, '#8c564b', '--'), (1.0, '#1f77b4', '-'), (2.0, '#d62728', '-'), (5.0, '#2ca02c', '-')]:
        t, y = solve(20.0, B0, 30.0, 7.0, 30.0)
        ax.plot(t, y[0], color=c, ls=ls, lw=2, label=f'剂量 D={B0}×')
    ax.axhline(1.0, color='red', ls=':', lw=1.5, label='WHO 阈值 1 μg/L')
    ax.plot(t, 20 * np.exp(-0.25 * t * np.exp(-0.1 * t) * 1.5), color='grey', lw=0, alpha=0)
    ax.set_xlabel('时间 (h)'); ax.set_ylabel('MC-LR (μg/L)')
    ax.set_title('(a) 不同投放剂量下的降解轨迹（C0=20 μg/L, 30℃, pH7）')
    ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.set_yscale('log'); ax.set_ylim(0.5, 40)
    ax = axes[1]
    for T, c in [(25, '#1f77b4'), (30, '#d62728'), (35, '#2ca02c'), (37, '#9467bd')]:
        t, y = solve(10.0, 1.0, T, 7.0, 30.0)
        ax.plot(t, y[0], color=c, lw=2, label=f'T={T}℃')
    ax.axhline(1.0, color='red', ls=':', lw=1.5)
    ax.set_xlabel('时间 (h)'); ax.set_ylabel('MC-LR (μg/L)')
    ax.set_title('(b) 温度的影响（C0=10 μg/L, D=1×）')
    ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.set_yscale('log'); ax.set_ylim(0.5, 20)
    ax = axes[2]
    for pH, c in [(5, '#1f77b4'), (7, '#d62728'), (9, '#2ca02c')]:
        t, y = solve(10.0, 1.0, 30.0, pH, 30.0)
        ax.plot(t, y[0], color=c, lw=2, label=f'pH={pH}')
    ax.axhline(1.0, color='red', ls=':', lw=1.5)
    ax.set_xlabel('时间 (h)'); ax.set_ylabel('MC-LR (μg/L)')
    ax.set_title('(c) pH 的影响（C0=10 μg/L, D=1×）')
    ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.set_yscale('log'); ax.set_ylim(0.5, 20)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig4_simulated_trajectories.png'), dpi=160)
    plt.close()

# ================================================================ 图5：剂量-时间等值线
def fig5_contour():
    C0s = np.logspace(np.log10(2.0), np.log10(120), 70)
    Ds = np.logspace(np.log10(0.2), np.log10(6.0), 55)
    TT = np.full((len(Ds), len(C0s)), np.nan)
    for i, D in enumerate(Ds):
        for j, C0 in enumerate(C0s):
            TT[i, j] = time_to_safety(C0, D, t_max=72.0)
    levs = [0, 1, 2, 4, 8, 12, 24, 48, 72]
    fig, ax = plt.subplots(figsize=(8.4, 6.4))
    cs = ax.contourf(C0s, Ds, TT, levels=levs, cmap='RdYlGn_r', extend='max')
    csl = ax.contour(C0s, Ds, TT, levels=levs[1:-1], colors='k', linewidths=0.9)
    ax.clabel(csl, fmt='%.0f h', fontsize=8)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(C0s.min(), C0s.max()); ax.set_ylim(Ds.min(), Ds.max())
    ax.set_xlabel('初始 MC-LR 浓度 C0 (μg/L, log)')
    ax.set_ylabel('投放剂量 D（m6 当量倍率, log）')
    ax.set_title('治理时间等值线图 t_安全(C0, D)（30℃, pH7；目标=WHO 阈值 1 μg/L）\n'
                 '白色区域=72 h 内无法达标；黑色等值线为治理时间(h)')
    ax.annotate('剂量不足/\n无法达标', xy=(60, 0.35), fontsize=8.5, color='#555')
    cbar = plt.colorbar(cs, ax=ax, ticks=levs[1:-1], extendrect=True)
    cbar.set_label('达到 1 μg/L 所需时间 (h)')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig5_dose_time_contour.png'), dpi=160)
    plt.close()

# ================================================================ 图6：不确定性传播
def fig6_uncertainty():
    fig, ax = plt.subplots(figsize=(8.6, 5.8))
    n = 400
    ks = np.random.lognormal(mean=np.log(0.25), sigma=0.35, size=n)
    Ts = np.random.normal(28.5, 1.8, n)
    pHs = np.random.normal(7.2, 0.5, n)
    ts = np.linspace(0, 24, 200)
    curves = np.zeros((n, len(ts)))
    for i in range(n):
        B0 = 1.0
        k = ks[i]
        # 使用该样本参数求解（单步近似解：C(t)=C0*exp(-k*B(t)*fT*fpH*dt 积分)）
        ft = f_T(Ts[i]) * f_pH(pHs[i])
        B_t = B0 * np.exp(-0.10 * ts)
        integ = np.cumsum(B_t) * (ts[1] - ts[0])
        curves[i] = 20.0 * np.exp(-k * ft * integ)
    q = np.percentile(curves, [5, 25, 50, 75, 95], axis=0)
    ax.fill_between(ts, q[0], q[4], color='#1f77b4', alpha=0.18, label='90% 区间')
    ax.fill_between(ts, q[1], q[3], color='#1f77b4', alpha=0.30, label='50% 区间')
    ax.plot(ts, q[2], color='#1f77b4', lw=2.5, label='中位预测')
    ax.axhline(1.0, color='red', ls=':', lw=1.5, label='WHO 阈值 1 μg/L')
    eps = 0.01
    t_med = np.where(q[2] <= 1.0)[0]
    ax.axvspan(0, 12, color='grey', alpha=0.06)
    ax.set_xlabel('时间 (h)'); ax.set_ylabel('MC-LR (μg/L)')
    ax.set_title('贝叶斯/蒙特卡洛不确定性传播：C0=20 μg/L, D=1×\n(k~LogN(0.25,σ=0.35), T~N(28.5,1.8), pH~N(7.2,0.5))')
    ax.set_yscale('log'); ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.set_ylim(0.5, 40)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig6_uncertainty_band.png'), dpi=160)
    plt.close()

# ================================================================ 图1：总体架构图
def fig1_architecture():
    fig, ax = plt.subplots(figsize=(13.2, 8.6))
    ax.set_xlim(0, 13); ax.set_ylim(0, 9); ax.axis('off')

    def box(x, y, w, h, text, fc='#eaf2fb', ec='#3b6ea5', fs=8.6):
        p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.06', fc=fc, ec=ec, lw=1.4)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, wrap=True)

    def arrow(x1, y1, x2, y2, text='', color='#333', fs=7.2):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=14, lw=1.3, color=color)
        ax.add_patch(a)
        if text:
            ax.text((x1 + x2) / 2 + 0.1, (y1 + y2) / 2, text, fontsize=fs, color=color, ha='left')

    ax.text(6.5, 8.62, 'MC-LR 降解动力学模型 —— 总体架构（灰箱混合模型：机理 ODE 内核 + 贝叶斯校准 + 决策优化）',
            ha='center', fontsize=12, fontweight='bold')

    # L1 数据层
    box(0.25, 7.1, 6.0, 1.15, 'L1 数据与知识层\n• 文献动力学参数库（mlrA/B/C/D 活性、株间速率、k_app）\n• 环境数据（检测节点/历史水质：T、pH、DO、浊度、光强）\n• 湿实验校准数据（降解实验：C(t)、B(t)、OD、产物）\n• 分子数据（mlr 基因/蛋白序列、表达 fold-change）', fc='#fff6e5', ec='#c98a2b')
    box(6.75, 7.1, 6.0, 1.15, 'L1b 观测与输入接口\n• C0: 检测节点荧光标准曲线（多时间点校准表 Ti(x)）\n• 投放决策上下文：无人机载荷、时效要求、水动力学\n• 先验信息（株系识别、表达强度、培养条件）', fc='#fff6e5', ec='#c98a2b')

    # L2 机理层
    box(0.25, 5.05, 6.0, 1.6, 'L2 机理内核（ODE 状态空间）\n状态：C(环状MC-LR)→L(线性)→P(四肽)→Adda/碎片；B(菌密度)；E(活性酶)\ndC/dt = −k_cat·E·C/(K_m+C)·f_T·f_pH·f_DO·θ_光死亡\n菌群：dB/dt = μ·B·S/(K_s+S) − δ_光(t)·B（YF1-FixJ 光控自杀约束）\n酶：dE/dt = α·B·(诱导) − β·E（mlr 表达动态，Adda/Hill 诱导）', fc='#e8f6ea', ec='#2e8b57')
    box(6.75, 5.05, 6.0, 1.6, 'L2b 环境等效修正模块（乘性/贝叶斯函数）\n• 温度钟形 f_T(T)：最适 30℃，20℃≈0.5×、37℃≈0.6×、>38℃≈0\n• pH 钟形 f_pH(pH)：最适 7，pH5≈0.44×、pH9≈0.5×\n• 溶解氧 DO、光照（自杀开关 δ(t)）、浊度/附着\n• 从 BBD-RSM（YF1）与单因子实验（m6）校准', fc='#fdeef2', ec='#c0508c')

    # L3 校准层
    box(0.25, 3.2, 6.0, 1.4, 'L3 参数估计与不确定性量化\n• 层次贝叶斯（Hierarchical Bayesian）：株间共享先验 + 株级随机效应\n• MCMC/HMC（NumPyro/Stan）或 ABC；惩罚复杂度\n• 参数可辨识性分析（profile likelihood / Sloppy matrix）\n• 预测分布（后验预测检查 PPC），输出 90% PI', fc='#ecf0ff', ec='#4a6ac0')
    box(6.75, 3.2, 6.0, 1.4, 'L3b 混合 ML / 代理层（可插拔）\n• GP/XGBoost 仿真代理：秒级 t_安全(C0,D,T,pH)\n• 残差学习（ML 修正机理模型偏差，如共降解/基质效应）\n• 可选 PINN/神经 ODE：数据充足时端到端估计\n• 迁移学习：文献株 → 本项目工程菌（株因子）', fc='#ecf0ff', ec='#4a6ac0')

    # L4 决策层
    box(0.25, 1.35, 6.0, 1.4, 'L4 决策与治理规划引擎\n• 反问题：min 剂量 s.t. t_安全 ≤ 目标时限（风险约束）\n• 输出：投放剂量 D*、预计治理时间 t*、分段投放策略\n• 灵敏度分析（Sobol/一阶+总效应）→ 关键不确定性排序\n• 安全弃权：置信不足/不可行 → 升级处置建议(二次投放/物理干预)', fc='#f7eefb', ec='#8b4ac0')
    box(6.75, 1.35, 6.0, 1.4, 'L4b 系统耦合接口\n• 与 2D 水流水质模型：降解作为汇项 S=−r(C,B,T,pH)\n• 与浓度预测/预警模型（XGBoost+LGBM 集成）衔接\n• 与无人机调度/路径规划：载荷建议、投放时序\n• 输出协议 JSON + 不确定性字段（对齐 plan.md 接口 B）', fc='#f7eefb', ec='#8b4ac0')

    # 底部
    box(0.25, 0.3, 12.5, 0.62, 'L0 工程实现：Python (scipy solve_ivp LSODA) + NumPyro（贝叶斯）+ scikit-learn/XGBoost（代理）｜JSON 接口｜版本化参数库与回归测试｜可部署于中控/边缘',
         fc='#f2f2f2', ec='#666666')

    arrow(3.3, 7.1, 3.3, 6.65, '')
    arrow(9.75, 7.1, 9.75, 6.65, '')
    arrow(3.3, 5.05, 3.3, 4.6, '')
    arrow(9.75, 5.05, 9.75, 4.6, '')
    arrow(3.3, 3.2, 3.3, 2.75, '')
    arrow(9.75, 3.2, 9.75, 2.75, '')
    ax.text(12.35, 6.05, '数据流', fontsize=8, color='#333', ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig1_overall_architecture.png'), dpi=160)
    plt.close()

# ================================================================ 图2：mlr 通路图
def fig2_pathway():
    fig, ax = plt.subplots(figsize=(12.6, 5.4))
    ax.set_xlim(0, 12.6); ax.set_ylim(0, 5.4); ax.axis('off')
    ax.text(6.3, 5.15, 'MC-LR 生物降解通路（mlr 酶级联）与降解菌生命周期的耦合', ha='center', fontsize=11.5, fontweight='bold')

    def box(x, y, w, h, text, fc, ec, fs=8.4):
        p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05', fc=fc, ec=ec, lw=1.3)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs)

    def arrow(x1, y1, x2, y2, label=''):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=13, lw=1.3, color='#333')
        ax.add_patch(a)
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.10, label, fontsize=7.6, ha='center')

    # 上排：底物/产物
    box(0.3, 3.2, 2.1, 1.2, 'MC-LR（环状七肽）\nAdda-Arg 键\n毒性：抑制 PP1/PP2A\n→ C 状态（环状）', '#fdeef2', '#c0508c')
    box(2.9, 3.2, 2.2, 1.2, '线性化 MC-LR\nMlrA 水解 Adda-Arg\n（毒力显著下降）\n→ L 状态', '#e8f6ea', '#2e8b57')
    box(5.6, 3.2, 2.2, 1.2, '四肽 + 可变肽段\nMlrB（丝氨酸蛋白酶）\n→ P 状态', '#e8f6ea', '#2e8b57')
    box(8.3, 3.2, 2.2, 1.2, 'Adda 等小分子/氨基酸\nMlrC（羧肽酶）\n→ X 状态（无毒末端）', '#e8f6ea', '#2e8b57')
    box(11.0, 3.2, 1.3, 1.2, '碳/氮源\n（供菌群生长）\nAdda 转氨酶', '#fff6e5', '#c98a2b')
    arrow(2.4, 3.8, 2.9, 3.8, 'MlrA\nkcat/Km')
    arrow(5.1, 3.8, 5.6, 3.8, 'MlrB')
    arrow(7.8, 3.8, 8.3, 3.8, 'MlrC')
    arrow(10.5, 3.8, 11.0, 3.8, '同化')

    # 下排：菌群与酶
    box(0.3, 1.1, 3.0, 1.5, '降解菌群 B(t)\n• 投放剂量 D（换算为 CFU/L）\n• 生长：μ·B·S/(K_s+S)（CQ5 型）\n或维持型（不做碳源时 μ≈0）\n• 死亡：δ(t)（YF1-FixJ 光控自杀\n → 自然光强 I(t)、水温耦合）', '#e8f0fb', '#3b6ea5')
    box(3.8, 1.1, 3.0, 1.5, 'mlr 酶表达 E(t)\n• 诱导：Adda/Hill 上调 mlrA/B（m6：1h 内 mlrA 上调 25 倍）\n• 组成型/诱导型可调（工程菌设计）\n• 表达-活性传递函数（蛋白量→kcat）\n• 失活：温度/蛋白水解', '#e8f0fb', '#3b6ea5')
    box(7.2, 1.1, 3.0, 1.5, '环境修正（乘性）\n• f_T(T)：钟形 30℃\n• f_pH(pH)：钟形 7\n• f_DO(DO)：有氧依赖\n• 光-死亡项 δ(I)\n• 基质/共降解竞争\n• 浊度/附着/吸附（沉积物汇）', '#fdf3e3', '#c98a2b')
    box(10.6, 1.1, 1.7, 1.5, '剂量-时长\n决策\nD*, t*', '#f7eefb', '#8b4ac0')

    arrow(1.8, 3.2, 1.8, 2.6, '酶催化中心')
    arrow(5.3, 3.2, 5.3, 2.6, '')
    arrow(8.6, 3.2, 8.6, 2.6, '')
    ax.text(6.3, 0.55, '注：MlrA 可将 MC-LR/RR/YR 在 Adda-Arg 处开环；对 MC-LA/LW/LY/LF 为 Adda-L-氨基酸位点；亦降解 Nodularin（10.1021/acs.chemrestox.3c00341）。',
            ha='center', fontsize=8, color='#555')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig2_mlr_pathway.png'), dpi=160)
    plt.close()

if __name__ == '__main__':
    fig1_architecture()
    fig2_pathway()
    fig3_literature()
    fig4_trajectories()
    fig5_contour()
    fig6_uncertainty()
    print('figures done ->', FIG_DIR)
    for f in sorted(os.listdir(FIG_DIR)):
        print(' ', f)
