import urllib.request, os, time
dirp = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\report\references'
urls = [
  ('https://www.mdpi.com/2220-9964/9/2/94/pdf', 'Donghu_MIKE21_MDPI_ijgi9020094.pdf'),
  ('https://www.mdpi.com/2073-4441/11/3/604/pdf', 'Koparan2019_UAV_water_sampling_Water11_604.pdf'),
  ('https://www.mdpi.com/1424-8220/23/16/7264/pdf', 'Sensors2023_UAV_coverage_23_7264.pdf'),
]
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
       'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
       'Referer': 'https://www.mdpi.com/'}
for u, name in urls:
    try:
        req = urllib.request.Request(u, headers=hdr)
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
        open(os.path.join(dirp, name), 'wb').write(data)
        print('OK', name, len(data))
    except Exception as e:
        print('FAIL', name, type(e).__name__, str(e)[:80])
    time.sleep(2)
