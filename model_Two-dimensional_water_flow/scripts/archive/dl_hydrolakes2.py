import urllib.request, os, sys
url = 'https://data.hydrosheds.org/file/hydrolakes/HydroLAKES_polys_v10_shp.zip'
out = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\data\raw\HydroLAKES_polys_v10_shp.zip'
req = urllib.request.Request(url, headers={'User-Agent': 'iGEM-DryLab/1.0'})
with urllib.request.urlopen(req, timeout=1200) as r:
    total = int(r.headers.get('Content-Length', 0))
    print('content-length:', total)
    got = 0
    with open(out, 'wb') as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk: break
            f.write(chunk); got += len(chunk)
print('downloaded:', got)
ok = False
try:
    import zipfile
    ok = zipfile.is_zipfile(out)
except Exception as e:
    print('zip check err', e)
print('is_zipfile:', ok)
