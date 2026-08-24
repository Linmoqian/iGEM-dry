# -*- coding: utf-8 -*-
"""
swflow.domain - East Lake (Wuhan) model domain: OSM-based water mask + synthetic bathymetry.
Coordinate system: local Cartesian (m), origin at (LON0, LAT0), equirectangular projection.
"""
import json, os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
RAW = os.path.join(ROOT, 'data', 'raw')
PROC = os.path.join(ROOT, 'data', 'processed')
FIG = os.path.join(ROOT, 'figures')
os.makedirs(PROC, exist_ok=True); os.makedirs(FIG, exist_ok=True)

LAT0 = 30.5566
LON0 = 114.3956
MLAT = 111320.0
MLON = 111320.0 * math.cos(math.radians(LAT0))

INCLUDE = ['东湖','水果湖','汤菱湖','庙湖','筲箕湖','小潭湖','小谭湖','官桥湖','郭郑湖','团湖','后湖','牛巢湖','喻家湖']
EXCLUDE = ['沙湖','南湖','杨春湖','严西湖','青菱湖','野芷湖','汤逊湖','黄家湖','长江']
BBOX = dict(lon_min=114.335, lon_max=114.462, lat_min=30.500, lat_max=30.608)

def ring_area_km2(pts):
    lat0 = sum(p[1] for p in pts)/len(pts); mlo = 111320*math.cos(math.radians(lat0))
    s = 0.0; n = len(pts)
    for i in range(n):
        x1,y1 = pts[i][0]*mlo, pts[i][1]*111320
        x2,y2 = pts[(i+1)%n][0]*mlo, pts[(i+1)%n][1]*111320
        s += x1*y2-x2*y1
    return abs(s)/2/1e6

def assemble_rings(seqs):
    """chain ways sharing end-nodes into closed loops; seqs: list of node-id lists"""
    used = [False]*len(seqs)
    loops = []
    for i in range(len(seqs)):
        if used[i]: continue
        chain = list(seqs[i]); used[i] = True
        # grow
        while True:
            end = chain[-1]
            found = False
            for j in range(len(seqs)):
                if used[j]: continue
                s = seqs[j]
                if not s: continue
                if s[0] == end and len(s) > 1:
                    chain.extend(s[1:]); used[j] = True; found = True; break
                if s[-1] == end and len(s) > 1:
                    chain.extend(reversed(s[:-1])); used[j] = True; found = True; break
            if not found:
                break
        if len(chain) >= 4 and chain[0] == chain[-1]:
            loops.append(chain)
        elif len(chain) >= 4:
            # try closing by appending first
            pass
    return loops

def load_osm():
    data = json.load(open(os.path.join(RAW, 'osm_rings.json'), encoding='utf-8'))
    coords = {int(k): v for k, v in data['nodes'].items()}
    ways = {int(k): v for k, v in data['ways'].items()}
    rels = {int(k): v for k, v in data['rels'].items()}
    polys = []
    # relations
    for rid, rel in rels.items():
        outer = [ways[w] for w in rel['outer'] if w in ways]
        inner = [ways[w] for w in rel['inner'] if w in ways]
        o_loops = assemble_rings(outer)
        i_loops = assemble_rings(inner)
        polys.append({'name': rel['name'], 'outer': o_loops, 'inner': i_loops})
    # standalone closed ways (not part of relations)
    used = set()
    for rel in rels.values():
        for w in rel['outer'] + rel['inner']:
            used.add(w)
    for wid, seq in ways.items():
        if wid in used: continue
        if len(seq) >= 4:
            polys.append({'name': '', 'outer': [seq], 'inner': []})
    # convert loops to lon/lat points
    result = []
    for p in polys:
        def loop_pts(loop):
            return [coords[n] for n in loop if n in coords]
        outer = [loop_pts(l) for l in p['outer']]
        inner = [loop_pts(l) for l in p['inner']]
        outer = [o for o in outer if len(o) >= 3]
        inner = [i for i in inner if len(i) >= 3]
        if outer:
            result.append({'name': p['name'], 'outer': outer, 'inner': inner})
    return result

def poly_area_km2(p):
    return sum(ring_area_km2(x) for x in p['outer']) - sum(ring_area_km2(x) for x in p['inner'])

def select_polys(polys):
    keep = []
    for p in polys:
        name = p['name'].strip()
        area = poly_area_km2(p)
        if area < 0.05: continue
        if name in EXCLUDE: continue
        allpts = [pt for ring in p['outer'] for pt in ring]
        lons = [pt[0] for pt in allpts]; lats = [pt[1] for pt in allpts]
        if not lons: continue
        if min(lons) < BBOX['lon_min'] or max(lons) > BBOX['lon_max'] or min(lats) < BBOX['lat_min'] or max(lats) > BBOX['lat_max']:
            continue
        clon = sum(lons)/len(lons); clat = sum(lats)/len(lats)
        if clat < 30.528 and clon < 114.372: continue
        if name in INCLUDE or (area >= 0.12):
            keep.append((name, area, p))
    return keep

def project(lon, lat):
    return (lon-LON0)*MLON, (lat-LAT0)*MLAT

def rasterize_mask(sel, dx, xmin, xmax, ymin, ymax):
    nx = int(round((xmax-xmin)/dx)); ny = int(round((ymax-ymin)/dx))
    xs = xmin + (np.arange(nx)+0.5)*dx
    ys = ymin + (np.arange(ny)+0.5)*dx
    XX, YY = np.meshgrid(xs, ys)
    pts = np.column_stack([XX.ravel(), YY.ravel()])
    mask = np.zeros((ny, nx), bool)
    for name, area, p in sel:
        for ring in p['outer']:
            pp = [project(lo, la) for lo, la in ring]
            if len(pp) < 3: continue
            m = Path(pp).contains_points(pts).reshape(ny, nx)
            mask |= m
        for ring in p['inner']:
            pp = [project(lo, la) for lo, la in ring]
            if len(pp) < 3: continue
            m = Path(pp).contains_points(pts).reshape(ny, nx)
            mask &= ~m
    return mask, xs, ys

def build_bathymetry(mask, dx, mean_depth, max_depth, seed_L=6.0):
    dist = distance_transform_edt(mask) * dx
    def mean_for_L(L):
        return (max_depth*(1.0-np.exp(-dist/L)))[mask].mean() - mean_depth
    lo, hi = seed_L, 2000.0
    if mean_for_L(lo) <= 0:
        lo = 0.5; hi = seed_L
    for _ in range(80):
        mid = 0.5*(lo+hi)
        if mean_for_L(mid) > 0: lo = mid
        else: hi = mid
    L = 0.5*(lo+hi)
    depth = np.where(mask, max_depth*(1.0-np.exp(-dist/L)), 0.0)
    return depth, L, dist

def main(dx=50.0, mean_depth=2.21, max_depth=4.75):  # Donghu survey values (Li et al. 2020, doi:10.3390/ijgi9020094)
    polys = load_osm()
    sel = select_polys(polys)
    total = sum(a for _, a, _ in sel)
    print('selected: %d polygons, raw area sum %.2f km2' % (len(sel), total))
    allp = [pt for _,_,p in sel for ring in p['outer'] for pt in ring]
    lons = [pt[0] for pt in allp]; lats = [pt[1] for pt in allp]
    x_min, _ = project(min(lons), 0); x_max, _ = project(max(lons), 0)
    _, y_min = project(0, min(lats)); _, y_max = project(0, max(lats))
    pad = 400.0
    mask, xs, ys = rasterize_mask(sel, dx, x_min-pad, x_max+pad, y_min-pad, y_max+pad)
    area_km2 = mask.sum()*dx*dx/1e6
    print('grid: %s, wet cells: %d, area: %.2f km2' % (mask.shape, mask.sum(), area_km2))
    depth, L, dist = build_bathymetry(mask, dx, mean_depth, max_depth)
    print('bathymetry L=%.2f mean=%.2f max=%.2f' % (L, depth[mask].mean(), depth[mask].max()))
    np.savez_compressed(os.path.join(PROC, 'domain.npz'), mask=mask, depth=depth, xs=xs, ys=ys, dx=dx)
    with open(os.path.join(PROC, 'domain_meta.json'), 'w', encoding='utf-8') as f:
        json.dump({'dx': dx, 'lat0': LAT0, 'lon0': LON0, 'area_km2': float(area_km2),
                   'grid_shape': [int(v) for v in mask.shape], 'depth_L': float(L),
                   'mean_depth_target': mean_depth, 'max_depth': max_depth}, f, ensure_ascii=False, indent=1)
    import matplotlib.font_manager as fm
    for _f in ('C:/Windows/Fonts/simhei.ttf', 'C:/Windows/Fonts/msyh.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'):
        if os.path.exists(_f):
            fm.fontManager.addfont(_f)
            break
    plt.rcParams['font.family'] = 'SimHei' if os.path.exists('C:/Windows/Fonts/simhei.ttf') else 'sans-serif'
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
    ax = axes[0]
    ax.imshow(mask, origin='lower', extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap='Blues', vmin=0, vmax=1)
    ax.set_title('武汉东湖水域掩膜 (OSM, 50m网格)  面积=%.1f km2' % area_km2, fontsize=13)
    ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)')
    ax2 = axes[1]
    im = ax2.imshow(depth, origin='lower', extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap='YlGnBu')
    ax2.set_title('重构水深 (m) 均值=%.2f 最大=%.2f (标定目标 2.21/4.75m)' % (depth[mask].mean(), depth[mask].max()), fontsize=13)
    ax2.set_xlabel('x (m)')
    fig.colorbar(im, ax=ax2, shrink=0.8)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG, 'fig01_domain_mask_depth.png'), dpi=130)
    print('figure saved')

if __name__ == '__main__':
    main()
