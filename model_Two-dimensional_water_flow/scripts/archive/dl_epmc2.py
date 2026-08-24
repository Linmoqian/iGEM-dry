import urllib.request, json, os, time
dirp = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\report\references'
u = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.3390/ijgi9020094&format=json'
d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'iGEM/1.0'}), timeout=60).read().decode())
for r_ in d.get('resultList', {}).get('result', []):
    print('EPMC:', r_.get('pmcid'), r_.get('title'), r_.get('isOpenAccess'))
    pc = r_.get('pmcid')
    if pc:
        url = 'https://europepmc.org/articles/%s?pdf=render' % pc
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 Chrome/126.0'}), timeout=180).read()
        if len(data) > 20000:
            open(os.path.join(dirp, 'Donghu_MIKE21_MDPI_ijgi9020094.pdf'), 'wb').write(data)
            print('OK pdf', len(data))
