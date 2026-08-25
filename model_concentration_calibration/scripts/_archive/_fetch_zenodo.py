import json, urllib.request, os, time
DL = r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/datasets'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode('utf-8', errors='replace')
for rid in ['17566822', '4025048', '17341156', '17807781']:
    try:
        raw = get('https://zenodo.org/api/records/' + rid + '?size=1')
        j = json.loads(raw)
        print('===', rid, ':', j['metadata']['title'][:80])
        for f in j['files']:
            name_clean = f['key'].replace('/', '_').replace(':', '_')
            out = os.path.join(DL, rid + '_' + name_clean)
            print('  file:', f['key'], round(f['size']/1024), 'KB')
            if os.path.exists(out): print('    skip (exists)'); continue
            try:
                data = get(f['links']['self'])
                open(out, 'wb').write(data.encode('latin-1')) if False else None
                # download binary properly
                req = urllib.request.Request(f['links']['self'], headers={'User-Agent': UA})
                with urllib.request.urlopen(req, timeout=300) as rr:
                    open(out, 'wb').write(rr.read())
                print('    OK', os.path.getsize(out), 'bytes')
            except Exception as e:
                print('    DL FAIL:', e)
            time.sleep(5)
    except Exception as e:
        print('===', rid, 'ERR', e)
    time.sleep(10)