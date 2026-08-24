
import json, urllib.request, urllib.parse, os
out_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(out_dir, exist_ok=True)
q = '[out:json][timeout:60];(way["name"~"东湖"](30.48,114.28,30.64,114.48);rel["name"~"东湖"](30.48,114.28,30.64,114.48););out geom center tags;'
data = urllib.parse.urlencode({'data': q}).encode()
req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data,
    headers={'User-Agent': 'iGEM-DryLab-Research/1.0 (education)'})
try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        d = json.loads(resp.read().decode())
        with open(os.path.join(out_dir, 'osm_enghu_raw.json'), 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False)
        print('saved osm_enghu_raw.json, elements:', len(d.get('elements', [])))
        for el in d.get('elements', []):
            t = el.get('tags', {})
            print(f"{el['type']} id={el['id']} name={t.get('name')} en={t.get('name:en')} natural={t.get('natural')} center={el.get('center', {})} npts={len(el.get('geometry', el.get('members', [])))}")
except Exception as e:
    print('FAIL:', e)
