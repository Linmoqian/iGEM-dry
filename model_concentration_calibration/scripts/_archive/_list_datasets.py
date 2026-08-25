import json, urllib.request, urllib.parse
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (research)'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

def zenodo(q, size=15):
    url = 'https://zenodo.org/api/records?' + urllib.parse.urlencode({'q': q, 'size': size, 'sort': 'mostrecent'})
    try:
        d = get(url)
        print(f'### Zenodo query: {q}  hit_count={d.get("hits",{}).get("total",0)}')
        for it in d.get('hits',{}).get('hits',[]):
            m = it.get('metadata',{})
            files = it.get('files',[])
            fs = ', '.join(f'{f["key"]} ({f["size"]//1024}KB)' for f in files[:4])
            acc = m.get('access_right','?')
            print(f'- [{it["id"]}] {m.get("title","?")[:110]} | doi={it.get("doi","?")} | access={acc}')
            print(f'    files: {fs}')
    except Exception as e:
        print(f'ERR zenodo {q}: {e}')

for q in ['microcystin', 'cyanotoxin', '"microcystin" AND "fluorescence"', 'harmful algal bloom dataset']:
    zenodo(q)

def figshare(search):
    url = 'https://api.figshare.com/v2/articles/search'
    body = json.dumps({'search_for': search, 'page_size': 10}).encode()
    req = urllib.request.Request(url, data=body, headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            items = json.loads(r.read().decode('utf-8'))
        print(f'### Figshare search: {search}  n={len(items)}')
        for it in items:
            print(f'- [{it.get("id")}] {it.get("title","?")[:100]} | doi={it.get("doi","?")} | size={it.get("total_size",0)//1048576}MB | dl={it.get("download_count","?")}')
    except Exception as e:
        print(f'ERR figshare {search}: {e}')

for s in ['microcystin', 'cyanobacteria toxin water quality', 'fluorescence biosensor raw data']:
    figshare(s)