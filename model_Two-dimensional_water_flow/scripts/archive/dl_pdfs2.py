import urllib.request, json, os, time
dirp = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\report\references'
dois = {
 '10.3390/ijgi9020094': 'Donghu_MIKE21_MDPI_ijgi9020094.pdf',
 '10.3390/w11030604': 'Koparan2019_UAV_water_sampling_Water11_604.pdf',
 '10.3390/s23167264': 'Sensors2023_UAV_coverage_23_7264.pdf',
}
for doi, name in dois.items():
    try:
        u = 'https://api.semanticscholar.org/graph/v1/paper/DOI:%s?fields=openAccessPdf' % doi
        req = urllib.request.Request(u, headers={'User-Agent':'iGEM-DryLab/1.0'})
        d = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
        pdf = (d.get('openAccessPdf') or {}).get('url')
        print(doi, '->', pdf)
        if pdf:
            req2 = urllib.request.Request(pdf, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0'})
            data = urllib.request.urlopen(req2, timeout=180).read()
            open(os.path.join(dirp, name), 'wb').write(data)
            print('  OK', name, len(data))
    except Exception as e:
        print(doi, 'FAIL', type(e).__name__, str(e)[:100])
    time.sleep(3)
