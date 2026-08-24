
import json, os
p = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'osm_lakes_full.json')
d = json.load(open(p, encoding='utf-8'))
els = d.get('elements', [])
types = {}
for el in els:
    types[el['type']] = types.get(el['type'], 0) + 1
print('types:', types)
rels = [el for el in els if el['type'] == 'relation']
print('n_rels:', len(rels))
for el in rels[:12]:
    ms = el.get('members', [])
    print(f"REL {el['id']} name={el.get('tags',{}).get('name')} members={len(ms)} with_geom={sum(1 for m in ms if m.get('geometry'))}")
ways = [el for el in els if el['type'] == 'way']
print('n_ways:', len(ways), 'with_geom:', sum(1 for w in ways if w.get('geometry')))
# check a way that likely belongs to 东湖 relation: find ways with name
named = [w for w in ways if w.get('tags', {}).get('name')]
print('named ways:', len(named))
for w in named[:10]:
    print(' WAY', w['id'], w['tags'].get('name'), 'npts', len(w.get('geometry', [])))
