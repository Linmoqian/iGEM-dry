import urllib.request, json, os
base = os.path.join(r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\data\raw')
os.makedirs(base, exist_ok=True)
url='https://archive-api.open-meteo.com/v1/archive?latitude=30.557&longitude=114.404&start_date=2023-01-01&end_date=2024-12-31&hourly=wind_speed_10m,wind_direction_10m,temperature_2m&timezone=Asia%2FShanghai'
req=urllib.request.Request(url, headers={'User-Agent':'iGEM-DryLab/1.0'})
d=json.loads(urllib.request.urlopen(req,timeout=120).read().decode())
with open(os.path.join(base,'openmeteo_wind_enghu_2023_2024.json'),'w',encoding='utf-8') as f:
    json.dump(d,f,ensure_ascii=False)
print('hours:', len(d['hourly']['time']), 'first:', d['hourly']['time'][0], 'last:', d['hourly']['time'][-1])
