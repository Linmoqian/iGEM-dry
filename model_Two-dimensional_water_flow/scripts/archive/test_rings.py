
import json, os, math
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
poly = json.load(open(os.path.join(RAW, 'osm_all_polys.json'), encoding='utf-8'))
LAT0=30.5566; LON0=114.3956
MLAT=111320.0; MLON=111320.0*math.cos(math.radians(LAT0))

def assemble_rings(way_seqs):
    """chain ways sharing end-nodes into closed rings"""
    used = [False]*len(way_seqs)
    rings = []
    for i in range(len(way_seqs)):
        if used[i]: continue
        chain = list(way_seqs[i]); used[i] = True
        while True:
            end = chain[-1] if chain else None
            found = False
            for j in range(len(way_seqs)):
                if used[j]: continue
                s = way_seqs[j]
                if not s: continue
                if s[0] == end:
                    chain.extend(s[1:]); used[j] = True; found = True; break
                elif s[-1] == end:
                    chain.extend(reversed(s[:-1])); used[j] = True; found = True; break
            if not found: break
        if len(chain) >= 3 and chain[0] == chain[-1]:
            rings.append(chain)
    return rings

# Build way seqs from stored osm data (need node ids per way + coords); we have osm_lakes_body.json saved with way nodes and node coords
body = json.load(open(os.path.join(RAW, 'osm_lakes_body.json'), encoding='utf-8'))
ways = {el['id']: el for el in body['elements'] if el['type']=='way'}
nodes = {el['id']: (el['lon'], el['lat']) for el in body['elements'] if el['type']=='node'}
print('ways:', len(ways), 'nodes:', len(nodes))
# relations with members: earlier saved osm_lakes_bbox.json does not have members... use polygon json? It has only rings per way.
# We need relation members: refetch quickly
print('need relation members; checking osm_lakes_bbox.json')
bbox = json.load(open(os.path.join(RAW, 'osm_lakes_bbox.json'), encoding='utf-8'))
rels = [el for el in bbox['elements'] if el['type']=='relation']
print('rels:', [(r['id'], r.get('tags',{}).get('name')) for r in rels])
