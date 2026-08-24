# -*- coding: utf-8 -*-
import io, os
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\MODEL_ARCHITECTURE.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("| 网格 dx | 50 m | 岸线系数 K=5.03 下折中 | 100 m 对照（待补） |",
              "| 网格 dx | 50 m | 岸线系数 K=5.03 下折中 | 100 m 对照（未来） |")
s = s.replace("| Manning n | 0.022 | 鄱阳湖研究区间 0.02–0.04 中值 | ±50% 影响（待补） |",
              "| Manning n | 0.022 | 鄱阳湖研究区间 0.02–0.04 中值 | n=0.015/0.030 实测（§11.3） |")
s = s.replace("| 涡黏 ν | 0.5 m²/s | 工程常用（Smagorinsky 替代列入未来） | 0.1–2 影响（待补） |",
              "| 涡黏 ν | 0.5 m²/s | 工程常用（Smagorinsky 替代列入未来） | 定性结论（§11.4） |")
# also mention 400m in section 5.2? the depth_L is ~498m - ok
io.open(p, 'w', encoding='utf-8').write(s)
print('param table patched')
# check no leftover placeholders
import re
leftovers = [m for m in re.findall(r'待回填|（待补）|XXX|TODO', s)]
print('leftovers:', leftovers)
