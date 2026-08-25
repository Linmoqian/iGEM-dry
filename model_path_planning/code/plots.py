# -*- coding: utf-8 -*-
"""
plots.py — 报告插图生成 (全部 PNG, 300dpi)
依赖: matplotlib; 自动侦测中文字体。
"""
import os, json, glob, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

CWD = os.path.dirname(os.path.abspath(__file__))
# V2.7 归档: 输出统一指向 experiments/V2.7_pathplanning (2026-08-25 整理)
ARCH = os.path.join(CWD, "..", "..", "model_Two-dimensional_water_flow", "report", "experiments", "V2.7_pathplanning")
OUT = os.path.join(ARCH, "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

sys_path = os.path.join(CWD)
import sys
sys.path.insert(0, sys_path)


def save(fig, name, dpi=200):
    p = os.path.join(OUT, name)
    try:
        fig.savefig(p, dpi=dpi, bbox_inches="tight", facecolor="white")
    except MemoryError:
        print("mem retry", name)
        fig.savefig(p, dpi=dpi // 2, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", p)


def fig1_system():
    fig, ax = plt.subplots(figsize=(12, 6.8))
    ax.axis("off")
    boxes = [
        ("① 漂浮检测节点\n(工程菌+荧光传感)", 0.02, 0.78, 0.42, 0.17),
        ("② 信号回传/风险预测\n(ML量化+浓度预测)", 0.02, 0.52, 0.42, 0.17),
        ("③ 任务级路径规划\n(本模型)", 0.02, 0.24, 0.42, 0.21),
        ("④ 无人机执行\n(投放降解菌)", 0.56, 0.78, 0.40, 0.17),
        ("⑤ 降解+监测回访\n(闭环反馈)", 0.56, 0.52, 0.40, 0.17),
        ("⑥ 调度/重规划\n(事件驱动+滚动时域)", 0.56, 0.24, 0.40, 0.21),
    ]
    for t, x, y, w, h in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                    linewidth=1.6, edgecolor="#1f77b4", facecolor="#eaf3fb"))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=12, fontweight="bold")
    ax.annotate("", xy=(0.56, 0.865), xytext=(0.44, 0.865), arrowprops=dict(arrowstyle="->", lw=2, color="#d62728"))
    ax.text(0.5, 0.885, "报警(≥1μg/L)", ha="center", fontsize=11, color="#d62728")
    ax.annotate("", xy=(0.72, 0.78), xytext=(0.72, 0.69), arrowprops=dict(arrowstyle="->", lw=2, color="#1f77b4"))
    ax.annotate("", xy=(0.48, 0.605), xytext=(0.44, 0.605), arrowprops=dict(arrowstyle="->", lw=2, color="#1f77b4"))
    ax.text(0.46, 0.625, "风险等级/预期扩散\n(阈值+优先级)", ha="center", fontsize=10)
    ax.annotate("", xy=(0.56, 0.345), xytext=(0.44, 0.345), arrowprops=dict(arrowstyle="->", lw=2.4, color="#2ca02c"))
    ax.text(0.5, 0.365, "最优/近优航线分配", ha="center", fontsize=11, color="#2ca02c")
    ax.annotate("", xy=(0.72, 0.52), xytext=(0.72, 0.45), arrowprops=dict(arrowstyle="->", lw=2, color="#2ca02c"))
    ax.annotate("", xy=(0.44, 0.24 + 0.105), xytext=(0.56, 0.24 + 0.105), arrowprops=dict(arrowstyle="->", ls="--", lw=1.4, color="#9467bd"))
    ax.text(0.5, 0.205, "新警报/状态变化 → 触发重规划", ha="center", fontsize=10, color="#9467bd")
    ax.text(0.5, 0.055, "任务级路径规划模型嵌入位置：监测-预警-规划-投放-降解 闭环中的③环节",
            ha="center", fontsize=12, fontweight="bold", color="#333")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "fig1_system_loop.png")


def fig2_model():
    fig, ax = plt.subplots(figsize=(12.5, 7.6))
    ax.axis("off")
    def box(x, y, w, h, t, fc="#eef7f0", ec="#2e7d32", fs=10.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012", lw=1.5, ec=ec, fc=fc))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)
        return (x, y, w, h)
    def arr(p1, p2, color="#2e7d32", ls="-", lw=1.6):
        ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", lw=lw, color=color, linestyle=ls))
    box(0.02, 0.62, 0.20, 0.30, "场景状态\n- 风险点(坐标/风险w/软窗)\n- 停机坪/无人机(载荷/电量)\n- 风场修正飞时矩阵 T[k,i,j]\n- 已服务/剩余需求", fs=9.5)
    box(0.02, 0.18, 0.20, 0.30, "动态事件\n- 新警报(泊松流)\n- 状态回传(装置/无人机)\n- 预测更新(SPO联动)", fs=9.5)
    box(0.28, 0.70, 0.20, 0.22, "Transformer 编码器\nL=3 · d=128 · H=8\n(节点特征+类型嵌入)", fs=10)
    box(0.54, 0.70, 0.25, 0.22, "多智能体指针解码器\n每步联合选择(无人机k,目标j)\n上下文=图嵌入+各机状态", fs=10)
    box(0.54, 0.44, 0.25, 0.20, "约束掩码\n载荷/能量(含返航)\n软时间窗/需求/停机坪", fs=10)
    box(0.54, 0.18, 0.25, 0.20, "POMO-lite 训练\n多采样共享基线\nREINFORCE(负目标奖励)", fs=10)
    box(0.84, 0.70, 0.15, 0.22, "构造解\n(每机访问序列\n含补货回站)", fs=10)
    box(0.84, 0.44, 0.15, 0.20, "后处理\n2-opt/relocate\n(改进即接受)", fs=10)
    box(0.84, 0.18, 0.15, 0.20, "滚动时域\n事件驱动\n增量重规划", fs=10)
    box(0.02, 0.02, 0.97, 0.10, "统一评分器 env.objective = Σ w_i·t_i + λ·Σ w_i·max(0,t_i−l_i) + μ·makespan + ν·未服务惩罚\n(与贪心/OR-Tools 共用，保证所有方法可比)", fs=10.5)
    arr((0.22, 0.77), (0.28, 0.81)); arr((0.22, 0.33), (0.54, 0.30), color="#7b1fa2")
    arr((0.48, 0.81), (0.54, 0.81)); arr((0.61, 0.70), (0.61, 0.665), color="#1565c0")
    arr((0.61, 0.44), (0.61, 0.39), color="#1565c0")
    arr((0.61, 0.28), (0.54, 0.28), color="#7b1fa2")
    arr((0.79, 0.81), (0.84, 0.81)); arr((0.79, 0.55), (0.84, 0.55)); arr((0.79, 0.28), (0.84, 0.28))
    arr((0.91, 0.70), (0.91, 0.66)); arr((0.91, 0.44), (0.91, 0.40))
    arr((0.60, 0.13), (0.60, 0.10), color="#555"); arr((0.44, 0.17), (0.44, 0.11), color="#555")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "fig2_model_architecture.png")


def fig3_scenario(seed=9001):
    sys.path.insert(0, sys_path)
    from scenario import build_eastlake, load_osm_water, DEPOTS
    from env import build_instance_from_scenario
    from solvers import greedy_solve
    fig, ax = plt.subplots(figsize=(8.4, 6.6))
    polys = load_osm_water()
    for name, pts in polys:
        if len(pts) < 3:
            continue
        pts = [(la, lo) for (la, lo) in pts if la is not None and lo is not None]
        if len(pts) < 3:
            continue
        lats = [p[0] for p in pts]; lons = [p[1] for p in pts]
        ax.plot(lons, lats, lw=0.4, color="#9ecae1", alpha=0.7)
    sc = build_eastlake(seed=seed, n_alerts=10, wind_hour=24)
    inst = build_instance_from_scenario(sc)
    rts = greedy_solve(inst)
    import math
    lat0, lon0 = 30.5667, 114.3833
    def deg(i):
        x, y = inst.xy[i]
        return lon0 + x / (111.320 * math.cos(math.radians(lat0))), lat0 + y / 110.574
    colors = ["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e"]
    for k, rt in enumerate(rts):
        seq = [int(inst.drone_depot[k])] + rt
        xs = [deg(i)[0] for i in seq]; ys = [deg(i)[1] for i in seq]
        ax.plot(xs, ys, "-", color=colors[k % 4], lw=1.8, alpha=0.9, label=f"无人机{k}航线", zorder=6)
    for i in range(inst.n_dep):
        dx, dy = deg(i)
        ax.scatter(dx, dy, marker="^", s=200, color="#333", zorder=7)
        ax.text(dx, dy + 0.004, DEPOTS[i][0], ha="center", fontsize=9, fontweight="bold", zorder=7)
    for j in inst.task_ids():
        w = inst.risk[j]
        c = "#d62728" if w > 0.4 else ("#ff7f0e" if w > 0.2 else "#2ca02c")
        dx, dy = deg(j)
        ax.scatter(dx, dy, marker="o", s=140 + 260 * w, color=c, zorder=6, alpha=0.92, edgecolor="white", linewidth=0.6)
    ax.set_xlim(114.30, 114.50); ax.set_ylim(30.51, 30.63)
    ax.set_xlabel("经度 (°E)"); ax.set_ylabel("纬度 (°N)")
    ax.set_title("图3 东湖应急投放场景：停机坪(▲) + 风险点(● 大小=风险权重) + 贪心示例航线", fontsize=12)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    p = os.path.join(OUT, "fig3_scenario_routes.png")
    fig.savefig(p, dpi=150, facecolor="white")
    plt.close(fig)
    print("saved", p)


def fig4_wind(seed=9001):
    sys.path.insert(0, sys_path)
    from scenario import build_eastlake
    from env import build_instance_from_scenario
    sc = build_eastlake(seed=seed, n_alerts=10, wind_hour=24)
    inst = build_instance_from_scenario(sc)
    T = inst.T[0]
    n = T.shape[0]
    d = T - T.T
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    im0 = axes[0].imshow(T, cmap="viridis")
    axes[0].set_title("图4a 飞行时间矩阵 T[i,j] (风修正, 非对称)")
    axes[0].set_xlabel("目标 j"); axes[0].set_ylabel("起点 i")
    plt.colorbar(im0, ax=axes[0], fraction=0.046)
    im1 = axes[1].imshow(d, cmap="RdBu_r", vmin=-np.max(np.abs(d)), vmax=np.max(np.abs(d)))
    axes[1].set_title("图4b 不对称程度 T[i,j]−T[j,i] (红=更顺风)")
    plt.colorbar(im1, ax=axes[1], fraction=0.046)
    for ax in axes:
        ax.set_xticks(range(n)); ax.set_yticks(range(n))
    save(fig, "fig4_wind_asymmetry.png")


def fig5_curve():
    p = os.path.join(ARCH, "trainings", "A", "train_curve.json")
    if not os.path.exists(p):
        print("skip fig5 (no curve yet)"); return
    d = json.load(open(p, encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ax.plot(d["step"], d["train_obj"], "o-", ms=3, label="训练批次目标 (采样均值)")
    ax.plot(d["step"], d["val_obj"], "s-", ms=3, label="验证集目标 (贪心解码)")
    ax.set_xlabel("训练步数"); ax.set_ylabel("目标值 (越小越好)")
    ax.set_title("图5 训练曲线：REINFORCE(多采样共享基线)")
    ax.legend(); ax.grid(alpha=0.3)
    save(fig, "fig5_training_curve.png")


def fig6_eval():
    p = os.path.join(ARCH, "results", "eval_results.json")
    if not os.path.exists(p):
        print("skip fig6 (no eval yet)"); return
    d = json.load(open(p, encoding="utf-8"))
    methods = list(d["methods"].keys())
    labels = {"greedy": "贪心", "greedy_ls": "贪心+局部搜索", "ortools": "OR-Tools",
              "rl_sampled": "RL(采样)", "rl_ls": "RL+局部搜索"}
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    mets = [("rwt", "风险加权投放时间 Σw·t (min)"), ("makespan", "最晚返回 makespan (min)"), ("obj", "综合目标值")]
    for ax, (key, title) in zip(axes, mets):
        vals = [d["methods"][m][key] for m in methods]
        cols = ["#9e9e9e", "#42a5f5", "#66bb6a", "#ef5350", "#ab47bc"][:len(methods)]
        ax.bar([labels.get(m, m) for m in methods], vals, color=cols)
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(title)
        ax.tick_params(axis="x", labelsize=8.5)
        for i, v in enumerate(vals):
            ax.text(i, v * 1.02, f"{v:.1f}", ha="center", fontsize=8.5)
    fig.suptitle("图6 东湖16场景评测：各路径规划方法对比", fontsize=13)
    fig.tight_layout()
    save(fig, "fig6_eval_comparison.png")


def fig7_pipeline():
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.axis("off")
    steps = [
        ("t0 警报事件流", "检测节点/预测模型\n产生(位置,风险,软窗)"),
        ("感知层\n状态快照", "风场/能量/载荷/时间"),
        ("规划层\n(本模型)", "NN构造解 +\n局部搜索精修"),
        ("执行层\n指挥下发", "各机路线 + 回站补货"),
        ("监控层\n偏差检测", "执行偏差/新警报\n/预测修正"),
        ("重规划触发?", "事件驱动条件:\n·新警报 Δw>阈值\n·偏差>5% 或\n·预测更新"),
    ]
    for i, (t, s) in enumerate(steps):
        x = 0.02 + i * 0.165
        ax.add_patch(FancyBboxPatch((x, 0.15), 0.145, 0.62, boxstyle="round,pad=0.01",
                                    lw=1.4, ec="#1565c0", fc="#e3f0fb"))
        ax.text(x + 0.0725, 0.66, t, ha="center", fontsize=10, fontweight="bold")
        ax.text(x + 0.0725, 0.36, s, ha="center", va="center", fontsize=8.6)
        if i < 5:
            ax.annotate("", xy=(x + 0.158, 0.46), xytext=(x + 0.146, 0.46),
                        arrowprops=dict(arrowstyle="->", lw=1.8, color="#1565c0"))
    ax.annotate("", xy=(0.025, 0.86), xytext=(0.94, 0.86),
                arrowprops=dict(arrowstyle="->", lw=1.6, color="#d81b60", connectionstyle="arc3,rad=-0.12"))
    ax.text(0.5, 0.92, "滚动时域重规划循环 (触发时仅对受影响子问题重解)", ha="center", fontsize=11, color="#d81b60")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "fig7_replan_pipeline.png")


if __name__ == "__main__":
    fig1_system(); fig2_model(); fig3_scenario(); fig4_wind(); fig7_pipeline()
    fig5_curve(); fig6_eval()
    print("ALL FIGURES DONE")
