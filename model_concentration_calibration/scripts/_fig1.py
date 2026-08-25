# figures.py — generate all report figures (run from repo root or with src on path)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import synth, calibrate as cal, forward as fw

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
os.makedirs(FIG, exist_ok=True)

d = synth.gen_dataset(seed=42)

def draw_box(ax, xy, w, h, text, fc='#eef3fa', ec='#33507a', fs=9):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle='round,pad=0.02', facecolor=fc, edgecolor=ec, lw=1.2, zorder=2))
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha='center', va='center', fontsize=fs, zorder=3)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8.6))
ax1.set_xlim(0, 14); ax1.set_ylim(0, 3.4); ax1.axis('off')
ax1.set_title('A. 信号链：从 MC-LR 浓度到电信号（物理链路 + 生物学链路）', fontsize=11, loc='left')

boxes = [('MC-LR\nC (ug/L)', 0.1), ('START核糖开关\n适配体识别', 1.5), ('LuxI/LuxR\n群体感应放大', 2.9), ('sfGFP/TurboRFP\nQ(t) 比值荧光', 4.3), ('LED激发+滤光\n光电二极管', 5.7), ('TIA+DeltaSigma ADC\n计数 y', 7.1), ('标定模型\nc_hat, CI, 预警', 8.5), ('中控+无人机\n投放决策', 9.9)]
w = 1.25; h = 1.5
for i, (txt, x) in enumerate(boxes):
    draw_box(ax1, (x, 0.9), w, h, txt, fc='#e8f4ea' if i in (0,7) else '#eef3fa')
    if i < len(boxes)-1:
        ax1.add_patch(FancyArrowPatch((x+w+0.02, 1.65), (x+w+0.28, 1.65), arrowstyle='-|>', mutation_scale=12, color='#33507a', lw=1.2))
ax1.text(0.1, 0.35, '生物学链路（分钟到小时级）', fontsize=9, color='#446699')
ax1.text(5.55, 0.35, '光学/电学链路（毫秒级）', fontsize=9, color='#446699')
ax1.text(8.3, 0.35, '模型层（毫秒级）', fontsize=9, color='#446699')
ax1.text(0.1, 2.8, '时变剂量-响应曲面 F(C,t) 与装置仿射 g,b 共同决定 y 到 C 的映射', fontsize=9, color='#666')
ax2.set_xlim(0, 14); ax2.set_ylim(0, 8.2); ax2.axis('off')
ax2.set_title('B. 模型架构：逐 trigger 的层次贝叶斯标定 + 融合反演 + 边缘部署', fontsize=11, loc='left')
draw_box(ax2, (0.1, 6.6), 2.4, 1.3, '湿实验数据\n(浓度 时间 重复 触发子 批次)', fc='#e8f4ea')
draw_box(ax2, (2.7, 6.6), 2.2, 1.3, '数据契约/QC\n空白扣减 OD 异常', fc='#fdf3e3')
draw_box(ax2, (5.08, 6.6), 2.2, 1.3, '折合比 F(c,t)\n=Q(c,t)/Q(0,t)', fc='#fdf3e3')
draw_box(ax2, (7.46, 6.6), 2.4, 1.3, '逐trigger参数化\n时变Hill(11参数)', fc='#eef3fa')
draw_box(ax2, (10.05, 6.6), 2.0, 1.3, 'MAP+Laplace\n后验采样', fc='#eef3fa')
draw_box(ax2, (0.1, 4.9), 2.4, 1.35, 'QC规则的\n可辨识域 旗标', fc='#fdf3e3')
draw_box(ax2, (2.7, 4.9), 2.2, 1.35, '装置仿射+串扰\n+温度暗基线', fc='#eef3fa')
draw_box(ax2, (5.08, 4.9), 2.2, 1.35, '多时间点\n似然融合', fc='#eef3fa')
draw_box(ax2, (7.46, 4.9), 2.4, 1.35, '后验 p(C|y,t)\n网格积分', fc='#eef3fa')
draw_box(ax2, (10.05, 4.9), 2.0, 1.35, 'P(C>=1ug/L)\n成本决策+等级', fc='#eef3fa')
draw_box(ax2, (0.1, 3.2), 2.4, 1.35, 'LOD/LOQ 覆盖率\n校准可靠性', fc='#eef3fa')
draw_box(ax2, (2.7, 3.2), 2.2, 1.35, '离线评估\nLOBO/蒙特卡洛', fc='#eef3fa')
draw_box(ax2, (5.08, 3.2), 2.2, 1.35, '机理先验\nQS-ODE合成数据', fc='#fdf3e3')
draw_box(ax2, (7.46, 3.2), 2.4, 1.35, '文献先验\n(1-2个数量级)', fc='#fdf3e3')
draw_box(ax2, (10.05, 3.2), 2.0, 1.35, '部署产物:\n参数+查找表JSON', fc='#e8f4ea')
draw_box(ax2, (3.0, 1.4), 3.4, 1.3, '云端/边端推理: 装置计数 -> affine -> 查找表 -> c_hat+区间+旗标', fc='#e8f4ea')
draw_box(ax2, (0.3, 0.2), 1.8, 0.9, '固件健康旗标:\n暗基线 LED 温度 饱和', fc='#fdf3e3', fs=8)
draw_box(ax2, (9.8, 0.2), 3.4, 0.9, '质量旗标: 低SNR 歧义 超量程 CI过宽', fc='#fdf3e3', fs=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig1_architecture.png'), dpi=170)
plt.close()
print('fig1 ok')