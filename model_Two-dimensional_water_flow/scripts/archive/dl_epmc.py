import urllib.request, os, time
dirp = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\report\references'
def get(u, name):
    try:
        req = urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0'})
        data = urllib.request.urlopen(req, timeout=180).read()
        if len(data) > 20000:
            open(os.path.join(dirp, name), 'wb').write(data)
            print('OK', name, len(data))
        else:
            print('SMALL', name, len(data), data[:80])
    except Exception as e:
        print('FAIL', name, type(e).__name__, str(e)[:90])
# europepmc render
get('https://europepmc.org/articles/PMC10458967?pdf=render', 'Sensors2023_UAV_coverage_23_7264.pdf')
# find PMC for Koparan via EPMC REST
try:
    u = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.3390/w11030604&format=json'
    d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'iGEM/1.0'}), timeout=60).read().decode())
    for r_ in d.get('resultList', {}).get('result', []):
        print('EPMC result:', r_.get('pmcid'), r_.get('title'))
except Exception as e:
    print('EPMC search fail', e)
time.sleep(2)
get('https://europepmc.org/articles/PMC6431723?pdf=render', 'Koparan2019_UAV_water_sampling_Water11_604.pdf')
