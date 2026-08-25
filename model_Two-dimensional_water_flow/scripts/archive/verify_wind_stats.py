# -*- coding: utf-8 -*-
import json, numpy as np, os
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\data\raw\openmeteo_wind_enghu_2023_2024.json'
d = json.load(open(p, encoding='utf-8'))
print('hourly_units:', d.get('hourly_units'))
print('keys:', list(d['hourly'].keys()))
spd = np.array(d['hourly']['wind_speed_10m'], float)
dirn = np.array(d['hourly']['wind_direction_10m'], float)
# convert if m/s already
u = spd.mean()
print('raw mean:', u, '=> m/s expected?')
# apply km/h -> m/s if unit says km/h
units = d.get('hourly_units', {}).get('wind_speed_10m', '')
if 'km' in units:
    spd = spd / 3.6
print('after unit conversion mean m/s =', spd.mean())
# stats
print('median', np.median(spd), 'p25', np.percentile(spd,25), 'p75', np.percentile(spd,75), 'p90', np.percentile(spd,90))
for thr in [0.5, 1.0, 2.0]:
    print('fraction < %.1f m/s: %.3f' % (thr, float((spd < thr).mean())))
# sectors (come-from)
sectors = ['N','NE','E','SE','S','SW','W','NW']
idx = ((dirn % 360) // 45).astype(int)
freq = np.bincount(idx, minlength=8)/len(dirn)
print('sector freq:', {s: round(float(f),4) for s,f in zip(sectors, freq)})
# circular mean for all & summer
def circ_mean(deg, m=None):
    th = np.radians(deg)
    if m is not None:
        return np.degrees(np.arctan2(np.nanmean(np.sin(th)*m), np.nanmean(np.cos(th)*m))) % 360
    return np.degrees(np.arctan2(np.mean(np.sin(th)), np.mean(np.cos(th)))) % 360
print('circ mean all:', round(float(circ_mean(dirn)),1))
tstr = d['hourly']['time']
months = np.array([int(t[5:7]) for t in tstr])
sum_ = months >= 6
print('summer mean spd: %.2f, summer circ mean: %.1f' % (float(spd[sum_].mean()), float(circ_mean(dirn[sum_]))))
print('winter (12,1,2) mean spd: %.2f, circ: %.1f' % (float(spd[(months==12)|(months<=2)].mean()), float(circ_mean(dirn[(months==12)|(months<=2)]))))
# daily cycle
hr = np.array([int(t[11:13]) for t in tstr])
print('mean by hour (CST):')
for h in [0,6,12,18,23]:
    print('  %02d: %.2f m/s from %.0f deg' % (h, float(spd[hr==h].mean()), float(circ_mean(dirn[hr==h]))))
