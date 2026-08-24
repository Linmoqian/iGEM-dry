
import json, urllib.request, urllib.parse, os
out_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
q = '[out:json][timeout:120];(rel["natural"="water"]["name"~"东湖|水果湖|汤菱湖|庙湖|筲箕湖|小谭湖|官桥湖|沙湖"](30.48,114.28,30.64,114.48);way["natural"="water"]["name"~"东湖|水果湖|汤菱湖|庙湖|筲箕湖|小谭湖|官桥湖|沙湖"](30.48,114.28,30.64,114.48););>;out body;'
data = urllib.parse.urlencode({'data': q}).encode()
req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data, headers={'User-Agent': 'iGEM-DryLab-Research/1.0 (education)'})
with urllib.request.urlopen(req, timeout=180) as resp:
    d = json.loads(resp.read().decode())
with open(os.path.join(out_dir, 'osm_lakes_body.json'), 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False)
els = d.get('elements', [])
from collections import Counter
print('elements:', len(els), Counter(el['type'] for el in els))
for el in els:
    if el['type'] == 'relation':
        ms = el.get('members', [])
        print('REL', el['id'], el.get('tags', {}).get('name'), 'members', len(ms))
