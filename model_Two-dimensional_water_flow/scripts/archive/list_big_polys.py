
import json, os, math
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
rows = []
for p in polys:
    a_out = sum(ring_area_km2(x) for x in p['rings']['outer'])
    a_in = sum(ring_area_km2(x) for x in p['rings']['inner'])
    area = a_out - a_in
    if area < 0.2: continue
    allpts = [pt for ring in p['rings']['outer'] for pt in ring]
    lons = [pt[0] for pt in allpts]; lats = [pt[1] for pt in allpts]
    rows.append((area, p['name'], min(lons), max(lons), min(lats), max(lats), len(p['rings']['outer'])))
rows.sort(reverse=True)
for area, name, lo, hi, la, ha, nw in rows:
    print(f"area={area:7.3f} name={name!r:12s} lon=[{lo:.4f},{hi:.4f}] lat=[{la:.4f},{ha:.4f}] outerways={nw}")
