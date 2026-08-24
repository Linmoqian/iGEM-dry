# -*- coding: utf-8 -*-
import geopandas as gpd, os, json
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\data\raw\hydrolakes\HydroLAKES_polys_v10_shp\HydroLAKES_polys_v10.shp'
gdf = gpd.read_file(p, bbox=(114.20, 30.40, 114.60, 30.70), rows=200000)
cen = gdf.geometry.centroid
gdf = gdf.assign(lon_cen=cen.x, lat_cen=cen.y)
sel = gdf[(gdf.lat_cen >= 30.48) & (gdf.lat_cen <= 30.63) & (gdf.lon_cen >= 114.30) & (gdf.lon_cen <= 114.50)]
out = []
for _, row in sel.iterrows():
    d = {c: row[c] for c in gdf.columns if c != 'geometry'}
    out.append({k: (None if isinstance(v, float) and v != v else v) for k, v in d.items()})
    print(row['Hylak_id'], '|', row.get('Lake_name'), '| area=%.2f' % (d.get('Lake_area') or 0), '| d_avg=%.2f' % (d.get('Depth_avg') or 0), '| elev=%.2f' % (d.get('Elevation') or 0), '| vol=%.4e' % (d.get('Vol_total') or 0), '| %.4f, %.4f' % (d['lon_cen'], d['lat_cen']))
json.dump(out, open(r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\data\raw\hydrolakes_eastlake_records.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print('saved json')
