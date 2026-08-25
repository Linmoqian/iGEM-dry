
import json, os
p = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'osm_lakes_full.json')
d = json.load(open(p, encoding='utf-8'))
els = d.get('elements', [])
ways = [el for el in els if el['type'] == 'way']
if ways:
    w = ways[0]
    print('way keys:', list(w.keys()))
    print(json.dumps(w, ensure_ascii=False)[:600])
nodes = [el for el in els if el['type'] == 'node'][:3]
print(json.dumps(nodes, ensure_ascii=False)[:400])
print('total nodes:', sum(1 for el in els if el['type']=='node'), 'ways:', len(ways))
