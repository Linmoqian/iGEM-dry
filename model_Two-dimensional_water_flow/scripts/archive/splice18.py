import io, os
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\MODEL_ARCHITECTURE.md'
s = io.open(p, encoding='utf-8').read()
new_sec = io.open(r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\scripts\new_section18.md', encoding='utf-8').read()
old = '## 18. 引用与数据来源\n\n- 文献：见 `report/文献综述.md`（含 DOI 与下载状态）。'
assert old in s
s = s.replace(old, new_sec + '\n## 19. 引用与数据来源\n\n- 文献：见 `report/文献综述.md`（含 DOI 与下载状态）。')
io.open(p, 'w', encoding='utf-8').write(s)
print('spliced ok')