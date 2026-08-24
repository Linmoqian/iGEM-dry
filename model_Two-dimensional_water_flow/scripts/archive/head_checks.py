import urllib.request
for u in [
 'https://data.hydrosheds.org/file/hydrolakes/HydroLAKES_polys_v10_shp.zip',
 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N30_00_E114_00_DEM/Copernicus_DSM_COG_10_N30_00_E114_00_DEM.tif']:
    try:
        req = urllib.request.Request(u, method='HEAD', headers={'User-Agent':'iGEM-DryLab/1.0'})
        r = urllib.request.urlopen(req, timeout=60)
        print(u.split('/')[-1], '->', r.status, 'len=', r.headers.get('Content-Length'), 'type=', r.headers.get('Content-Type'))
    except Exception as e:
        print(u.split('/')[-1], 'FAIL', e)
