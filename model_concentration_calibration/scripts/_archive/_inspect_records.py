import json, urllib.request
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))
for rec in ['17566822','4025048','17341156','17807781']:
    d = get('https://zenodo.org/api/records/' + rec)
    print(f'=== Zenodo {rec}: {d["metadata"]["title"][:100]}')
    for f in d.get('files',[]):
        print(f'  - {f["key"]} | {f["size"]//1024}KB | {f["links"]["self"]}')
for arts in ['32928698','32928701']:
    d = get('https://api.figshare.com/v2/articles/' + arts)
    print(f'=== Figshare {arts}: {d.get("title","")[:100]}')
    for f in d.get('files',[]):
        print(f'  - {f.get("name")} | {f.get("size",0)//1024}KB | {f.get("download_url")}')