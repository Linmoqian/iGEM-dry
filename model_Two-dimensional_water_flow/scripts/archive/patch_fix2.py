# -*- coding: utf-8 -*-
import io, os
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\README.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("38 m、31.2 km²（OSM 掩膜", "50 m 网格 31.2 km²（OSM 掩膜")
io.open(p, 'w', encoding='utf-8').write(s)
print('README fixed')
