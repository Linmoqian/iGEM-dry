# -*- coding: utf-8 -*-
"""
train.py — REINFORCE(POMO-lite: 多采样共享基线)训练任务级路径规划策略
用法: python train.py --steps 2000 --batch 16 --samples 8 --n-task 10
输出: out/ckpt.pt, out/train_curve.json, out/val_trajectory.json
"""
import argparse, json, os, sys, time, math
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario import build_eastlake
from env import build_instance_from_scenario, objective, risk_weighted_time
from model import PolicyNetwork

DEVICE = "cpu"
HORIZON = 180.0
REFILL = 12.0
HOVER = 0.13
DEMAND_MAX = 6.0


def inst_tensors(batch):
    n = max(len(i.xy) for i in batch)
    m = len(batch[0].drone_cap)
    B = len(batch)
    x = torch.zeros(B, n, 6)
    is_dep = torch.zeros(B, n, dtype=torch.long)
    T = torch.zeros(B, m, n, n)
    demand = torch.zeros(B, n)
    risk = torch.zeros(B, n)
    tw = torch.zeros(B, n)
    depot_of = torch.zeros(B, m, dtype=torch.long)
    cap = torch.zeros(B, m)
    en = torch.zeros(B, m)
    for b, inst in enumerate(batch):
        ni = len(inst.xy)
        xyz = torch.tensor(inst.xy, dtype=torch.float32)
        xyz = (xyz - xyz.mean(0)) / (xyz.std(0) + 1e-6)
        dn = torch.tensor(inst.demand, dtype=torch.float32)
        rk = torch.tensor(inst.risk, dtype=torch.float32)
        twv = torch.tensor(np.where(np.isfinite(inst.tw_end), inst.tw_end, inst.horizon), dtype=torch.float32)
        x[b, :ni, 0:2] = xyz
        x[b, :ni, 2] = dn / DEMAND_MAX
        x[b, :ni, 3] = rk
        x[b, :ni, 4] = twv / inst.horizon
        x[b, :ni, 5] = 0.0
        is_dep[b, :ni] = (torch.arange(ni) < inst.n_dep).long()
        T[b, :, :ni, :ni] = torch.tensor(inst.T, dtype=torch.float32)
        demand[b, :ni] = dn
        risk[b, :ni] = rk
        tw[b, :ni] = twv
        depot_of[b] = torch.tensor(inst.drone_depot, dtype=torch.long)
        cap[b] = torch.tensor(inst.drone_cap, dtype=torch.float32)
        en[b] = torch.tensor(inst.drone_energy, dtype=torch.float32)
    return dict(x=x, is_dep=is_dep, T=T, demand=demand, risk=risk, tw=tw,
                depot_of=depot_of, cap=cap, en=en)


def rollouts(policy, batch, S=8, greedy=False):
    """batch: list[Instance]; 返回 (logps:(B*S,), objs:(B*S,), routes_list, metas)"""
    t = inst_tensors(batch)
    B, m = t["cap"].shape
    n = t["x"].shape[1]
    h = policy.encode(t["x"], t["is_dep"])
    B2 = B * S
    rep = lambda z: z.repeat_interleave(S, dim=0) if z.dim() >= 1 else z
    h2 = rep(h)
    is_dep2 = rep(t["is_dep"]).bool().view(B2, n)
    T2 = rep(t["T"])
    demand2 = rep(t["demand"])
    depot2 = rep(t["depot_of"])
    cap2 = rep(t["cap"])
    en2 = rep(t["en"])
    served = torch.zeros(B2, n)
    cur = depot2.clone()
    cap_rem = cap2.clone()
    en_rem = en2.clone()
    tnow = torch.zeros(B2)
    logps = torch.zeros(B2)
    actions = [[] for _ in range(B2)]
    max_steps = min(2 * int(demand2.sum()) + 4 * m + 8, 100)
    total_demand = demand2.clone()
    arB = torch.arange(B2).view(B2, 1, 1)
    arM = torch.arange(m).view(1, m, 1)
    arN = torch.arange(n).view(1, 1, n)
    for step in range(max_steps):
        # 索引快照(避免 in-place 更新污染 autograd 版本计数)
        curc = cur.detach().clone()
        # leg/ret 矩阵
        T_leg = T2[arB, arM.expand(B2, m, n), curc.unsqueeze(-1).expand(B2, m, n), arN.expand(B2, m, n)]
        T_ret = T2[arB, arM.expand(B2, m, n), arN.expand(B2, m, n), depot2.unsqueeze(-1).expand(B2, m, n)]
        is_task = (~is_dep2).unsqueeze(1).expand(B2, m, n)      # (B2,m,n) j 是任务
        infeasible = torch.zeros(B2, m, n, dtype=torch.bool)
        # 任务规则
        served_ok = (served.unsqueeze(1) < demand2.unsqueeze(1)).expand(B2, m, n)
        load_ok = (cap_rem.unsqueeze(-1) >= 1.0).expand(B2, m, n)
        en_ok_task = (en_rem.unsqueeze(-1) - T_leg - T_ret) >= 0.0
        time_ok = (tnow.unsqueeze(-1).unsqueeze(-1).expand(B2, m, n) + T_leg) <= HORIZON
        infeasible = infeasible | (is_task & (~served_ok))
        infeasible = infeasible | (is_task & (~load_ok))
        infeasible = infeasible | (is_task & (~en_ok_task))
        infeasible = infeasible | (is_task & (~time_ok))
        # 停机坪规则: 仅本机停机坪 & 需要补给 & 不在停机坪 & 能量满足
        need_refill = ((cap_rem < 1.0) | (en_rem < 0.5 * en2)).unsqueeze(-1)
        dep_ok = (depot2.unsqueeze(-1) == arN.expand(B2, m, n)) & need_refill & (curc.unsqueeze(-1) != arN.expand(B2, m, n))
        en_ok_dep = (en_rem.unsqueeze(-1) - T_leg) >= 0.0
        infeasible = infeasible | ((~is_task) & (infeasible | (~dep_ok | ~en_ok_dep)))
        # 全部不可行 -> 终止(未服务计入惩罚)
        if infeasible.all():
            break
        logits = policy.logits(h2, curc, cap_rem, en_rem, tnow, infeasible)
        lsm = F.log_softmax(logits.reshape(B2, -1), dim=-1)
        if greedy:
            idx = lsm.argmax(dim=-1)
        else:
            idx = torch.multinomial(lsm.exp(), 1).squeeze(-1)
        logps = logps + lsm.gather(1, idx.unsqueeze(-1)).squeeze(-1)
        for b in range(B2):
            kk = int(idx[b] // n)
            jj = int(idx[b] % n)
            if jj != int(cur[b, kk]):
                leg = float(T2[b, kk, cur[b, kk], jj])
                tnow[b] += leg
                en_rem[b, kk] = max(0.0, float(en_rem[b, kk]) - leg)
                if jj == int(depot2[b, kk]):
                    cap_rem[b, kk] = cap2[b, kk]
                    en_rem[b, kk] = en2[b, kk]
                    tnow[b] += REFILL
                    actions[b].append((int(kk), jj))    # 停机坪补货
                else:
                    served[b, jj] += 1.0
                    cap_rem[b, kk] -= 1.0
                    tnow[b] += HOVER
                    actions[b].append((int(kk), jj))
                cur[b, kk] = jj
        if (served >= total_demand).all():
            break
    # 用 env.objective 统一评分 (从动作重建 routes)
    objs = np.zeros(B2)
    routes_list = []
    for b in range(B2):
        inst = batch[b // S]
        rts = [[] for _ in range(m)]
        for (k, j) in actions[b]:
            rts[k].append(j)
        routes_list.append(rts)
        o, _ = objective(inst, rts)
        objs[b] = o
    return logps, torch.tensor(objs, dtype=torch.float32), routes_list, None


def make_batch(seed, n_task, B, wind_hours):
    rng = np.random.RandomState(seed)
    batch = []
    for b in range(B):
        sc = build_eastlake(seed=seed * 997 + b, n_alerts=n_task, wind_hour=int(rng.choice(wind_hours)))
        batch.append(build_instance_from_scenario(sc))
    return batch


def eval_greedy(policy, n_inst=12, n_task=10, seed=12345):
    batch = make_batch(seed, n_task, n_inst, [0, 12, 36, 100, 200, 300])
    with torch.no_grad():
        logps, objs, routes_list, _ = rollouts(policy, batch, S=1, greedy=True)
    return float(objs.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--n-task", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--d", type=int, default=96)
    ap.add_argument("--L", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--out", type=str, default="out")
    args = ap.parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    policy = PolicyNetwork(d=args.d, L=args.L)
    opt = torch.optim.Adam(policy.parameters(), lr=args.lr)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out)
    os.makedirs(out_dir, exist_ok=True)
    curve = {"step": [], "train_obj": [], "val_obj": []}
    t0 = time.time()
    val_last = None
    for step in range(args.steps):
        batch = make_batch(seed=args.seed * 1000 + step, n_task=args.n_task, B=args.batch,
                           wind_hours=[0, 12, 36, 100, 200, 300, 800, 1400])
        logps, objs, rts, _ = rollouts(policy, batch, S=args.samples)
        objs_arr = objs.view(args.batch, args.samples)
        baseline = objs_arr.mean(dim=1, keepdim=True)
        adv = (baseline - objs_arr)                     # 优于基线的轨迹给正优势
        lp = logps.view(args.batch, args.samples)
        loss = -(adv.detach() * lp).mean()
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        opt.step()
        if step % 50 == 0 or step == args.steps - 1:
            val_obj = eval_greedy(policy, 12, args.n_task, seed=424242)
            curve["step"].append(step)
            curve["train_obj"].append(float(objs.mean()))
            curve["val_obj"].append(val_obj)
            print(f"step {step:5d} | train_obj {float(objs.mean()):8.2f} | val_obj {val_obj:8.2f} | t {time.time()-t0:7.1f}s", flush=True)
            val_last = val_obj
    torch.save(policy.state_dict(), os.path.join(out_dir, "ckpt.pt"))
    with open(os.path.join(out_dir, "train_curve.json"), "w", encoding="utf-8") as f:
        json.dump(curve, f)
    print(f"done. final val_obj={val_last:.2f}  total {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
