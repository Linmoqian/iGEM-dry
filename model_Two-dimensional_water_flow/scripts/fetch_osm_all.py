
import json, urllib.request, urllib.parse, os, math, time
base = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
def overpass(q, retries=6, wait=8):
    data = urllib.parse.urlencode({'data': q}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data,
                headers={'User-Agent': 'iGEM-DryLab-Research/1.0 (education)'})
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print('retry', i, type(e).__name__, str(e)[:80]); time.sleep(wait)
    raise RuntimeError('overpass failed: ' + q[:50])
q1 = '[out:json][timeout:240];(rel["natural"="water"](30.48,114.28,30.64,114.48);way["natural"="water"](30.48,114.28,30.64,114.48););out body;'
d1 = overpass(q1)
rels = {el['id']: el for el in d1['elements'] if el['type']=='relation'}
ways = {el['id']: el for el in d1['elements'] if el['type']=='way'}
print('rels:', len(rels), 'ways:', len(ways))
all_way_ids = set(w for w in ways)
for rel in rels.values():
    for m in rel.get('members', []):
        if m.get('type')=='way': all_way_ids.add(m.get('ref', -1))
all_way_ids.discard(-1)
q2 = '[out:json][timeout:240];way(id={});out body;'.format(','.join(map(str, sorted(all_way_ids))))
d2 = overpass(q2)
ways2 = {el['id']: el for el in d2['elements'] if el['type']=='way'}
node_ids = sorted({n for w in ways2.values() for n in w.get('nodes', [])})
coords = {}
for i in range(0, len(node_ids), 5000):
    ids = node_ids[i:i+5000]
    q3 = '[out:json][timeout:240];node(id={});out;'.format(','.join(map(str, ids)))
    d3 = overpass(q3)
    for el in d3['elements']:
        if el['type']=='node': coords[el['id']] = (el['lon'], el['lat'])
print('coords:', len(coords))
# assemble: polygons = list of {name, rings: outer[], inner[]}
polys = []
used_way_ids = set()
for rel in rels.values():
    rings = {'outer': [], 'inner': []}
    for m in rel.get('members', []):
        if m.get('type') != 'way': continue
        w = ways2.get(m.get('ref'))
        if not w: continue
        pts = [coords[n] for n in w.get('nodes', []) if n in coords]
        if len(pts) >= 3:
            rings[m.get('role','outer')].append(pts)
            used_way_ids.add(m.get('ref'))
    if rings['outer']:
        pollys = {'name': rel.get('tags',{}).get('name',''), 'rings': rings}
        polys.append(pollys)
for w in ways2.values():
    if w['id'] in used_way_ids: continue
    pts = [coords[n] for n in w.get('nodes',[]) if n in coords]
    if len(pts) >= 3:
        polys.append({'name': w.get('tags',{}).get('name',''), 'rings': {'outer':[pts], 'inner':[]}})
with open(os.path.join(base, 'osm_all_polys.json'), 'w', encoding='utf-8') as f:
    json.dump(polys, f, ensure_ascii=False)
def area_km2(pts):
    lat0 = sum(p[1] for p in pts)/len(pts); mlon = 111320.0*math.cos(math.radians(lat0))
    s=0.0; n=len(pts)
    for i in range(n):
        x1,y1=pts[i][0]*mlon,pts[i][1]*111320.0; x2,y2=pts[(i+1)%n][0]*mlon,pts[(i+1)%n][1]*111320.0
        s += x1*y2-x2*y1
    return abs(s)/2/1e6
for p in polys:
    a = sum(area_km2(x) for x in p['rings']['outer']) - sum(area_km2(x) for x in p['rings']['inner'])
    print(f"name={p['name']} area={a:.3f} km2  outer_ways={len(p['rings']['outer'])}")
