import json, os, subprocess
tmp = r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/_tmp.json'
DL = r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/datasets'
for rid in ['17566822', '4025048', '17341156', '17807781']:
    url = 'https://zenodo.org/api/records/' + rid + '?size=1'
    subprocess.run(['curl.exe', '-sSL', '--max-time', '90', '-A', 'Mozilla/5.0', '-o', tmp, url], check=False)
    try:
        j = json.load(open(tmp, encoding='utf-8'))
        print('===', rid, ':', j['metadata']['title'][:80])
        for f in j['files']:
            name_clean = f['key'].replace('/', '_').replace(':', '_')
            out = os.path.join(DL, rid + '_' + name_clean)
            print('  file:', f['key'], round(f['size']/1024), 'KB')
            if os.path.exists(out) and os.path.getsize(out) > 100:
                print('    skip (exists)')
                continue
            r = subprocess.run(['curl.exe', '-sSL', '--max-time', '300', '-A', 'Mozilla/5.0', '-o', out, f['links']['self']], capture_output=True)
            if os.path.exists(out) and os.path.getsize(out) > 100:
                print('    OK', os.path.getsize(out), 'bytes')
            else:
                print('    FAIL', r.returncode)
    except Exception as e:
        print('===', rid, 'ERR', e)