# -*- coding: utf-8 -*-
import json, numpy as np, os
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\data\raw\openmeteo_wind_enghu_2023_2024.json'
d = json.load(open(p, encoding='utf-8'))
spd = np.array(d['hourly']['wind_speed_10m'], float)/3.6
dirn = np.array(d['hourly']['wind_direction_10m'], float)
tstr = d['hourly']['time']
months = np.array([int(t[5:7]) for t in tstr])
def circ_mean(deg):
    th = np.radians(deg)
    return float(np.degrees(np.arctan2(np.mean(np.sin(th)), np.mean(np.cos(th)))) % 360)
print('monthly:')
for m in range(1, 13):
    sel = months == m
    if sel.sum():
        print('  %02d: mean %.2f m/s  circ %.1f deg  n=%d' % (m, float(spd[sel].mean()), circ_mean(dirn[sel]), int(sel.sum())))
sum_ = (months>=6)&(months<=8)
print('SUMMER Jun-Aug: mean %.2f circ %.1f' % (float(spd[sum_].mean()), circ_mean(dirn[sum_])))
win = (months==12)|(months<=2)
print('WINTER Dec-Feb: mean %.2f circ %.1f' % (float(spd[win].mean()), circ_mean(dirn[win])))
# per-sector mean speed & percentiles (scenario library)
sectors = ['N','NE','E','SE','S','SW','W','NW']
idx = ((dirn % 360) // 45).astype(int)
print('sector stats:')
for s, k in zip(sectors, range(8)):
    sel = idx == k
    print('  %s: freq %.3f  mean %.2f  p50 %.2f  p75 %.2f  p90 %.2f' % (s, float(sel.mean()), float(spd[sel].mean()), float(np.percentile(spd[sel],50)), float(np.percentile(spd[sel],75)), float(np.percentile(spd[sel],90))))
