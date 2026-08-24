# -*- coding: utf-8 -*-
import json, os, time, urllib.request, urllib.parse
RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
def overpass(q, retries=6, wait=8):
    data = urllib.parse.urlencode({'data': q}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data,
                headers={'User-Agent': 'iGEM-DryLab-Research/1.0 (education)'})
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print('retry', i, type(e).__name__, str(e)[:70]); time.sleep(wait)
    raise RuntimeError('overpass failed')
# known relevant relations + standalone ways from earlier queries
rel_ids = [1687983, 7160933, 20174744, 20174962, 20174963]
extra_way_ids = [103504237, 122747058, 881445354]
qB = '[out:json][timeout:240];rel(id={});out body;'.format(','.join(map(str, rel_ids)))
dB = overpass(qB)
rels = {el['id']: el for el in dB['elements'] if el['type'] == 'relation'}
way_ids = set(extra_way_ids)
for rel in rels.values():
    for m in rel.get('members', []):
        if m.get('type') == 'way' and m.get('ref'):
            way_ids.add(m['ref'])
way_ids = sorted(way_ids)
qC = '[out:json][timeout:240];way(id={});out body;'.format(','.join(map(str, way_ids)))
dC = overpass(qC)
ways = {el['id']: el for el in dC['elements'] if el['type'] == 'way'}
node_ids = sorted({n for w in ways.values() for n in w.get('nodes', [])})
coords = {}
for i in range(0, len(node_ids), 6000):
    ids = node_ids[i:i+6000]
    qD = '[out:json][timeout:240];node(id={});out;'.format(','.join(map(str, ids)))
    dD = overpass(qD)
    for el in dD['elements']:
        if el['type'] == 'node':
            coords[el['id']] = [el['lon'], el['lat']]
out = {'rels': {}, 'ways': {}, 'nodes': coords}
for rid, rel in rels.items():
    out['rels'][str(rid)] = {'name': rel.get('tags', {}).get('name', ''),
        'outer': [m['ref'] for m in rel.get('members', []) if m.get('type')=='way' and m.get('role','outer')=='outer'],
        'inner': [m['ref'] for m in rel.get('members', []) if m.get('type')=='way' and m.get('role')=='inner']}
for wid, w in ways.items():
    out['ways'][str(wid)] = w.get('nodes', [])
with open(os.path.join(RAW, 'osm_rings.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)
print('saved osm_rings.json: rels=%d ways=%d nodes=%d' % (len(out['rels']), len(out['ways']), len(coords)))
