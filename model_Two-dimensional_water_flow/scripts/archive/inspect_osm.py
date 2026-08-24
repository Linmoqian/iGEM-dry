
import json, os, math
p = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'osm_lakes_bbox.json')
d = json.load(open(p, encoding='utf-8'))
out = []
for el in d.get('elements', []):
    t = el.get('tags', {})
    typ = el['type']; eid = el['id']
    if typ == 'relation':
        members = el.get('members', [])
        n_outer = sum(1 for m in members if m.get('role')=='outer')
        n_inner = sum(1 for m in members if m.get('role')=='inner')
        n_geom = sum(1 for m in members if m.get('geometry'))
        out.append(f"REL id={eid} name={t.get('name')} members={len(members)} outer={n_outer} inner={n_inner} with_geom={n_geom}")
    else:
        geom = el.get('geometry', [])
        out.append(f"WAY id={eid} name={t.get('name')} npts={len(geom)}")
open(os.path.join(os.path.dirname(__file__), 'osm_summary.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
