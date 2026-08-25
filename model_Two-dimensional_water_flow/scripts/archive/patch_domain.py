
import re
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\src\swflow\domain.py'
s = open(p, encoding='utf-8').read()
s = s.replace('ax.set_title('East Lake (Donghu) water mask from OSM', 'ax.set_title("East Lake (Donghu) water mask (OSM, 50 m grid)"')
s = re.sub(r"\n(50 m grid)', fontsize=12)", "", s)
s = s.replace("ax2.set_title('Reconstructed depth (m)", 'ax2.set_title("Reconstructed depth (m)')
s = s.replace("%.2f % (depth[mask].mean(), depth[mask].max()), fontsize=12)", "%.2f" % (depth[mask].mean(), depth[mask].max()), fontsize=12)")
# remove leftover broken pieces
s = s.replace('(50 m grid)"', '')
open(p, 'w', encoding='utf-8').write(s)
print('patched')
