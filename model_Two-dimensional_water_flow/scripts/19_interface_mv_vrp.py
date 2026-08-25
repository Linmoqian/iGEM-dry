# -*- coding: utf-8 -*-
"""E4: pipeline-interface simulation — deployment module (Top-K drop points + expected
protection) -> multi-visit heterogeneous-drone scheduling, following the MV-VRP-MHD
formulation (Jiang et al. 2025, Transp. Res. Part C 172:105026) and the region
coverage-aware planning taxonomy (Kumar & Kumar 2023, Phys. Commun. 59:102073).
Drones: the path-planning module's fleet (cap 4/4/6 kg, endurance 28/28/34 min,
speed 15/15/13 m/s); time matrix wind-corrected (asymmetric) as in path planning.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
opt = dict(np.load(os.path.join(PROC, "opt_result.npz")))
cands, member_scores = opt["cands"], opt["member_scores"]
score = member_scores.mean(axis=0)
K = 8
order = np.argsort(-score)[:K]
pts_m = cands[order]
pts_score = score[order]
print("top-%d candidates (flow-model coords, m), expected protection:" % K)
for k in range(K):
    print("  #%d (%7.0f, %7.0f)  score=%.4f" % (k, pts_m[k,0], pts_m[k,1], pts_score[k]))

# --- coordinate frames: flow model (LON0=114.3956, LAT0=30.5566, equirect) ->
#     path-planning frame (LAKE_CENTER 30.5667,114.3833, km) ---
LON0, LAT0 = 114.3956, 30.5566
MLON = 111320.0*math.cos(math.radians(LAT0))
def flow_to_pp(x, y):
    lon = LON0 + x/MLON
    lat = LAT0 + y/111320.0
    return ((lon-114.3833)*111.320*math.cos(math.radians(30.5667)),
            (lat-30.5667)*110.574)   # km
tasks_xy = np.array([flow_to_pp(*p) for p in pts_m])
DEPOTS_PP = [("北岸", 30.5990, 114.3920), ("西南岸", 30.5400, 114.3560), ("东岸", 30.5620, 114.4250)]
fun = lambda la, lo: ((lo-114.3833)*111.320*math.cos(math.radians(30.5667)),
                       (la-30.5667)*110.574)
dep_xy = np.array([fun(la, lo) for _, la, lo in DEPOTS_PP])

# --- visits: dose demand per point (payload units, risk-dependent: higher score -> more dose)
demand = 1 + np.floor(2.0*pts_score/pts_score.max()).astype(int)   # 1..3 payloads
print("\nvisits per point (payload units, risk-proportional):", demand)
print("total payloads: %d" % demand.sum())

# --- wind-corrected asymmetric time matrix (same model as path_planning.wind_time_matrix)
WIND = np.array([-2.5*np.sin(math.radians(135.0)), -2.5*np.cos(math.radians(135.0))])  # m/s, SE wind
def time_matrix(xy, v0=15.0, wind=WIND, safety=1.25, hover=0.13):
    n = len(xy); T = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j: continue
            dvec = xy[j]-xy[i]; d = math.hypot(*dvec)*1000.0     # km -> m
            ux, uy = dvec/d
            vp = wind[0]*ux + wind[1]*uy
            vg = math.sqrt(max(v0**2 - (np.dot(wind, wind) - vp**2), 4.0)) + vp
            T[i, j] = safety*d/max(vg, 1.0)/60.0 + hover
    return T

n_d = len(dep_xy)
allxy = np.vstack([dep_xy, tasks_xy])
T = time_matrix(allxy)
print("\nT (min) [depot0 -> tasks]:", np.round(T[0, n_d:], 2))

# --- simple solver: list scheduling of visits with NN+2-opt routes (per drone capacity) ---
CAP = [4, 4, 6]; EN = [28.0, 28.0, 34.0]; SPD = [15.0, 15.0, 13.0]

def route_time(dep, visits, T, spd_k):
    n = len(visits)
    if n == 0: return 0.0, []
    # NN construction
    cl = list(visits); cur = dep; route = []
    while cl:
        j = int(np.argmin([T[cur, n_d+i] for i in cl]))
        i = cl.pop(j); route.append(i); cur = n_d+i
    # 2-opt improve (path cost + return)
    def cost(r):
        c = T[dep, n_d+r[0]] + sum(T[n_d+r[k], n_d+r[k+1]] for k in range(len(r)-1)) + T[n_d+r[-1], dep]
        return c*(15.0/spd_k)
    rr = list(route)
    improved = True
    while improved:
        improved = False
        for a in range(len(rr)-1):
            for b in range(a+1, len(rr)):
                r2 = rr[:a] + rr[a:b+1][::-1] + rr[b+1:]
                if cost(r2) < cost(rr) - 1e-9:
                    rr = r2; improved = True
    return cost(rr), rr

D = dict(drones=list(range(3)), done=np.zeros(3), fleet_T=[[] for _ in range(3)], fleet_R=[[] for _ in range(3)])
# visits list: repeat each point index demand[i] times
visits_all = []
for i in range(K):
    visits_all += [i]*demand[i]
np.random.default_rng(0)
visits_all = sorted(visits_all, key=lambda i: -pts_score[i])   # risk-priority order (coverage-aware)
schedule = [[] for _ in range(3)]; makespan = np.zeros(3)
rem = list(visits_all)
while rem:
    # greedy: assign to the drone with the smallest current makespan; fill one trip
    # while capacity and endurance allow (risk-priority order preserved)
    m = int(np.argmin(makespan))
    trip = []; cap_left = CAP[m]; t_now = makespan[m]
    i0 = 0
    while i0 < len(rem):
        i = rem[i0]
        if cap_left <= 0: break
        trips = trip + [i]
        t_rt, _ = route_time(0, trips, T, SPD[m])
        if t_now + t_rt > EN[m] and trip:
            break
        trip.append(i); cap_left -= 1; rem.pop(i0)
        i0 = 0
    if not trip:
        t_rt, r0 = route_time(0, [rem[0]], T, SPD[m])
        trip = [rem.pop(0)]
        makespan[m] += t_rt
        schedule[m].append(trip)
        continue
    t_rt, r0 = route_time(0, trip, T, SPD[m])
    schedule[m].append(r0)
    makespan[m] += t_rt
print("\nschedule (visit indices -> drop points; T in min):")
for m in range(3):
    tot = sum(len(r) for r in schedule[m])
    print("  drone%d (cap %d, %d min): %d sorties, %d payloads, elapsed %.1f min"
          % (m, CAP[m], EN[m], len(schedule[m]), tot, makespan[m]))
print("makespan (3 drones) = %.1f min" % makespan.max())

# single-drone baseline (cap 6)
def single_drone():
    rem = list(visits_all); t = 0.0; n_s = 0
    while rem:
        trip = []; cap = 6
        while rem and cap > 0:
            trip.append(rem.pop(0)); cap -= 1
        t_rt, _ = route_time(0, trip, T, 15.0)
        t += t_rt; n_s += 1
    return t, n_s
t1, n_s1 = single_drone()
print("single drone (cap 6 kg): %.1f min over %d sorties" % (t1, n_s1))
print("speed-up from 3-drone cooperation: %.2fx" % (t1/makespan.max()))

# objective: protected-area-weighted delivery rate
delivered = np.zeros(3)
for m in range(3):
    for r in schedule[m]:
        for i in r:
            delivered[m] += pts_score[i]*demand[i]  # proportional to dose delivered at i
tot_delivered = delivered.sum()
print("score-weighted delivered: %.4f ; per minute (3 drones): %.5f ; single: %.5f"
      % (tot_delivered, tot_delivered/makespan.max(), tot_delivered/t1))
