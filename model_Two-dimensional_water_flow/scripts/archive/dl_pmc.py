import urllib.request, os, time
dirp = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\report\references'
tests = [
 ('https://pmc.ncbi.nlm.nih.gov/articles/PMC10458967/pdf/sensors-23-07264.pdf', 'Sensors2023_UAV_coverage_23_7264.pdf'),
]
for u, name in tests:
    try:
        req = urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0'})
        data = urllib.request.urlopen(req, timeout=180).read()
        open(os.path.join(dirp, name), 'wb').write(data)
        print('OK', name, len(data))
    except Exception as e:
        print('FAIL', name, type(e).__name__, str(e)[:100])
