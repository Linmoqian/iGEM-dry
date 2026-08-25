import io, os
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\ARCHITECTURE_ITERATIONS.md'
s = io.open(p, encoding='utf-8').read()
new_sec = io.open(r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\scripts\new_rounds_26_30.md', encoding='utf-8').read()
s = s.rstrip() + chr(10) + chr(10) + new_sec
io.open(p, 'w', encoding='utf-8').write(s)
print('rounds appended')