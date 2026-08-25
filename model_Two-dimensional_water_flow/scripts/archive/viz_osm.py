
import json, os, math
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
polys = json.load(open(os.path.join(RAW, 'osm_all_polys.json'), encoding='utf-8'))
def ring_area_km2(pts):
    lat0 = sum(p[1] for p in pts)/len(pts); mlo = 111320*math.cos(math.radians(lat0))
    s = 0.0; n = len(pts)
    for i in range(n):
        x1,y1 = pts[i][0]*mlo, pts[i][1]*111320
        x2,y2 = pts[(i+1)%n][0]*mlo, pts[(i+1)%n][1]*111320
        s += x1*y2-x2*y1
    return abs(s)/2/1e6
LAT0=30.5566; LON0=114.3956
MLAT=111320.0; MLON=111320.0*math.cos(math.radians(LAT0))
fig, ax = plt.subplots(figsize=(13, 12))
colors = plt.cm.tab20(np.linspace(0, 1, 20))
k = 0
for p in polys:
    area = sum(ring_area_km2(x) for x in p['rings']['outer']) - sum(ring_area_km2(x) for x in p['rings']['inner'])
    if area < 0.15: continue
    c = colors[k % 20]
    for ring in p['rings']['outer']:
        pts = np.array([[(lo-LON0)*MLON, (la-LAT0)*MLAT] for lo, la in ring])
        ax.fill(pts[:,0], pts[:,1], color=c, alpha=0.45, lw=0.6, ec='k')
    allpts = [pt for ring in p['rings']['outer'] for pt in ring]
    lon = sum(pt[0] for pt in allpts)/len(allpts); lat = sum(pt[1] for pt in allpts)/len(allpts)
    ax.text((lon-LON0)*MLON, (lat-LAT0)*MLAT, f'{k}: {area:.1f}km2 {p["name"]}', fontsize=7, ha='center', color='darkred')
    k += 1
ax.set_aspect('equal'); ax.set_xlim(-26000, 14000); ax.set_ylim(-12000, 20000)
ax.set_title('OSM water polygons around East Lake (numbered, area km2)')
plt.tight_layout()
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'figures', 'tmp_osm_polygons.png'), dpi=110)
print('saved, n_polys>=0.15:', k)
