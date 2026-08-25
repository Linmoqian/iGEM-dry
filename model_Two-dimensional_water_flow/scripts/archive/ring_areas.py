
import json, math, os
base = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'osm_lakes_polygons.json')
d = json.load(open(base, encoding='utf-8'))
def ring_area_km2(pts):
    lat0 = sum(p[1] for p in pts)/len(pts)
    mlat = 111320.0; mlon = 111320.0*math.cos(math.radians(lat0))
    s = 0.0; n = len(pts)
    for i in range(n):
        x1,y1 = pts[i][0]*mlon, pts[i][1]*mlat
        x2,y2 = pts[(i+1)%n][0]*mlon, pts[(i+1)%n][1]*mlat
        s += x1*y2 - x2*y1
    return abs(s)/2/1e6
for rid, info in d.items():
    for role in ['outer','inner']:
        tot = sum(ring_area_km2(pts) for pts in info['rings'][role])
        print(rid, info['name'], role, 'total_km2=%.3f' % tot, 'n=', len(info['rings'][role]))
