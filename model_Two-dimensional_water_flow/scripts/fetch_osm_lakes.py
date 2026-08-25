
import json, urllib.request, urllib.parse, os
out_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
q = '[out:json][timeout:90];(rel["natural"="water"]["name"~"东湖|水果湖|汤菱湖|庙湖|筲箕湖|小谭湖|官桥湖|沙湖"](30.48,114.28,30.64,114.48);way["natural"="water"]["name"~"东湖|水果湖|汤菱湖|庙湖|筲箕湖|小谭湖|官桥湖|沙湖"](30.48,114.28,30.64,114.48););out geom center tags;'
data = urllib.parse.urlencode({'data': q}).encode()
req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data, headers={'User-Agent': 'iGEM-DryLab-Research/1.0 (education)'})
with urllib.request.urlopen(req, timeout=120) as resp:
    d = json.loads(resp.read().decode())
with open(os.path.join(out_dir, 'osm_lakes_bbox.json'), 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False)
print('elements:', len(d.get('elements', [])))
def poly_area(lonlat_list):
    # shoelace in approx m^2 via local scaling
    import math
    lat0 = sum(p[1] for p in lonlat_list)/len(lonlat_list)
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0*math.cos(math.radians(lat0))
    s = 0.0
    n = len(lonlat_list)
    for i in range(n):
        x1,y1 = lonlat_list[i][0]*m_per_deg_lon, lonlat_list[i][1]*m_per_deg_lat
        x2,y2 = lonlat_list[(i+1)%n][0]*m_per_deg_lon, lonlat_list[(i+1)%n][1]*m_per_deg_lat
        s += x1*y2 - x2*y1
    return abs(s)/2.0
for el in d.get('elements', []):
    t = el.get('tags', {})
    geom = el.get('geometry', [])
    if geom:
        pts = [(g['lon'], g['lat']) for g in geom]
        # outer ways only: relations contain members; compute per-way
        area = poly_area(pts)
        print(f"{el['type']} id={el['id']} name={t.get('name')} npts={len(pts)} area_km2={area/1e6:.3f}")
    else:
        print(f"{el['type']} id={el['id']} name={t.get('name')} (no geom, members={len(el.get('members',[]))})")
