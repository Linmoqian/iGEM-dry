
import json, urllib.request, urllib.parse, os, math, time
base = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
def overpass(q, retries=6, wait=8):
    data = urllib.parse.urlencode({'data': q}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data,
                headers={'User-Agent': 'iGEM-DryLab-Research/1.0 (education)'})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print('retry', i, type(e).__name__, e); time.sleep(wait)
    raise RuntimeError('overpass failed')
qB = '[out:json][timeout:120];rel(id=1687983,7160933,20174744,20174962,20174963);out body;'
dB = overpass(qB)
rels = {el['id']: el for el in dB.get('elements', []) if el['type'] == 'relation'}
all_way_ids = []
for rid, rel in rels.items():
    ms = rel.get('members', [])
    print('rel', rid, rel.get('tags', {}).get('name'), 'n_members', len(ms), 'sample', ms[:2])
    for m in ms:
        if m.get('type') == 'way' and m.get('ref'):
            all_way_ids.append(m['ref'])
all_way_ids = sorted(set(all_way_ids))
print('ways:', len(all_way_ids))
if all_way_ids:
    qC = '[out:json][timeout:120];way(id={});out body;'.format(','.join(map(str, all_way_ids)))
    dC = overpass(qC)
    ways = {el['id']: el for el in dC.get('elements', []) if el['type'] == 'way'}
    print('ways loaded:', len(ways))
    node_ids = sorted({n for w in ways.values() for n in w.get('nodes', [])})
    coords = {}
    for i in range(0, len(node_ids), 5000):
        ids = node_ids[i:i+5000]
        qD = '[out:json][timeout:120];node(id={});out;'.format(','.join(map(str, ids)))
        dD = overpass(qD)
        for el in dD.get('elements', []):
            if el['type'] == 'node':
                coords[el['id']] = (el['lon'], el['lat'])
    print('coords:', len(coords))
    result = {}
    for rid, rel in rels.items():
        name = rel.get('tags', {}).get('name')
        rings = {'outer': [], 'inner': []}
        for m in rel.get('members', []):
            if m.get('type') != 'way' or not m.get('ref'): continue
            w = ways.get(m['ref'])
            if not w: continue
            pts = []
            for nid in w.get('nodes', []):
                if nid in coords: pts.append(coords[nid])
            if len(pts) >= 3:
                rings[m.get('role', 'outer')].append(pts)
        result[rid] = {'name': name, 'rings': rings}
        print(f"rel {rid} name={name} outer_ways={len(rings['outer'])} inner_ways={len(rings['inner'])}")
    with open(os.path.join(base, 'osm_lakes_polygons.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
    print('saved')
