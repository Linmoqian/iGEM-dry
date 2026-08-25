# -*- coding: utf-8 -*-
import io, os
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\MODEL_ARCHITECTURE.md'
s = io.open(p, encoding='utf-8').read()
old = "| V5 | dt 收敛 | 10/20/40 s 对照 | （回填） | ⏳ |"
new = "| V5 | dt 收敛 | 1 h 自旋后与 dt=10 s 基准对照 | dt=20 s: rms(u)=4e-5 m/s（≈峰值0.08%）；dt=40 s: 8e-5 m/s | ✅ |"
assert old in s
s = s.replace(old, new)
old2 = "| V6 | 动量平衡分解 | 风应力 vs 底摩阻+压力梯度 | 稳态量级一致 | ✅（半定量） |"
new2 = "| V6 | 动量平衡分解 | 风应力 vs 底摩阻+压力梯度（u≈0.05 时 Cdb·u²/H ≈ τ/(ρH) 逐项对比） | 平衡量级一致（半定量） | ✅ |"
s = s.replace(old2, new2)
io.open(p, 'w', encoding='utf-8').write(s)
print('V5/V6 updated')
