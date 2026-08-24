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


def inst_tensors(batch, use_edge=False):
    n = max(len(i.xy) for i in batch)
    m = len(batch[0].drone_cap)
    B = len(batch)
    nf = 9 if use_edge else 6
    x = torch.zeros(B, n, nf)
    is_dep = torch.zeros(B, n, dtype=torch.long)
    T = torch.zeros(B, m, n, n)
    demand = torch.zeros(B, n)
    risk = torch.zeros(B, n)
    tw = torch.zeros(B, n)
    depot_of = torch.zeros(B, m, dtype=torch.long)
    cap = torch.zeros(B, m)
    en = torch.zeros(B, m)
    drone_w = torch.zeros(B, m)
    kappa = torch.ones(B, 1).float()
    e_res = torch.zeros(B, 1).float()
    pack_kg = 0.5
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
        if use_edge:
            # 特征5: 返航难度先验 (到最近停机坪距离/时域内最大航程)
            dep_xy = torch.tensor(inst.xy[:inst.n_dep], dtype=torch.float32)
            node_xy = torch.tensor(inst.xy, dtype=torch.float32)
            d_dep = torch.linalg.vector_norm(node_xy[:, None, :] - dep_xy[None, :, :], dim=-1).min(dim=1).values
            x[b, :ni, 5] = d_dep / 162.0   # 15 m/s × 180 min
            # 特征6-8: ANE-lite 边聚合 (RRNCO ANE 思想的聚合近似)
            Tmean = torch.tensor(inst.T, dtype=torch.float32).mean(0)          # (n,n) 机型平均
            scale = Tmean[Tmean > 0].median()
            e_in = Tmean.mean(0) / scale          # 到达 j 的平均成本
            e_out = Tmean.mean(1) / scale         # 从 j 出发的平均成本
            x[b, :ni, 6] = e_in[:ni]
            x[b, :ni, 7] = e_out[:ni]
            x[b, :ni, 8] = (e_in - e_out)[:ni]    # 非对称度 (风偏)
        else:
            x[b, :ni, 5] = 0.0
        is_dep[b, :ni] = (torch.arange(ni) < inst.n_dep).long()
        T[b, :, :ni, :ni] = torch.tensor(inst.T, dtype=torch.float32)
        demand[b, :ni] = dn
        risk[b, :ni] = rk
        tw[b, :ni] = twv
        depot_of[b] = torch.tensor(inst.drone_depot, dtype=torch.long)
        cap[b] = torch.tensor(inst.drone_cap, dtype=torch.float32)
        en[b] = torch.tensor(inst.drone_energy, dtype=torch.float32)
        if inst.drone_w is not None:
            drone_w[b] = torch.tensor(inst.drone_w, dtype=torch.float32)
            kappa[b] = float(inst.kappa)
            e_res[b] = float(inst.energy_reserve)
            pack_kg = float(inst.pack_kg)
    return dict(x=x, is_dep=is_dep, T=T, demand=demand, risk=risk, tw=tw,
                depot_of=depot_of, cap=cap, en=en, drone_w=drone_w, kappa=kappa,
                e_res=e_res, pack_kg=pack_kg)


def rollouts(policy, batch, S=8, greedy=False, anchor=False):
    """batch: list[Instance]; 返回 (logps:(B*S,), objs:(B*S,), routes_list, metas)
    anchor=True: 真 POMO 锚定 — 每个实例的 S 条轨迹分别强制'无人机0的首个目标=任务s'(不同起点)。
    use_edge/tanh_prior 从 policy 结构推断。
    """
    use_edge = policy.use_edge
    t = inst_tensors(batch, use_edge=use_edge)
    B, m = t["cap"].shape
    n = t["x"].shape[1]
    H = max(float(i.horizon) for i in batch)   # 批次内时域 (兼容 v3.0 flow 实例 480 min)
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
    W2 = rep(t["drone_w"])                                   # (B2,m) 空重; 全 0 = 未启用载荷耦合
    kappa2 = rep(t["kappa"]).expand(B2, m)
    res2 = rep(t["e_res"]).expand(B2, m)
    PKG = t["pack_kg"]
    use_payload = bool((W2 > 0).any())
    served = torch.zeros(B2, n)
    cur = depot2.clone()
    cap_rem = cap2.clone()
    en_rem = en2.clone()
    tnow = torch.zeros(B2, m)                       # F3 修复: 每机独立时钟 (B2, m)
    logps = torch.zeros(B2)
    actions = [[] for _ in range(B2)]
    max_steps = min(2 * int(demand2.sum()) + 4 * m + 8, 100)
    total_demand = demand2.clone()
    arB = torch.arange(B2).view(B2, 1, 1)
    arM = torch.arange(m).view(1, m, 1)
    arN = torch.arange(n).view(1, 1, n)
    T_scale = float(T2.max()) + 1e-6            # 边成本归一化尺度 (全批标量, 稳定)
    # 锚定任务: 实例内轨迹 s -> 任务 (s+b)%n_task (假设各实例任务数相同)
    anchor_j = None
    if anchor:
        n_task = int((~t["is_dep"].bool()).sum(dim=1).min())
        base = (torch.arange(S).view(1, S).repeat(B, 1) + torch.arange(B).view(B, 1)) % n_task
        base = base.reshape(B2)
        dep_cnt = t["is_dep"].sum(dim=1).min().long()
        anchor_j = base + dep_cnt + torch.arange(B2) * 0  # (B2,) 节点索引
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
        if use_payload:
            fac_leg = ((W2 + PKG * cap_rem) / W2.clamp(min=1e-6)) ** 1.5
            fac_ret = ((W2 + PKG * (cap_rem - 1.0).clamp(min=0.0)) / W2.clamp(min=1e-6)) ** 1.5
            en_leg = T_leg * fac_leg.unsqueeze(-1)
            en_ret = T_ret * fac_ret.unsqueeze(-1)
        else:
            en_leg = T_leg
            en_ret = T_ret
        en_ok_task = (en_rem.unsqueeze(-1) - en_leg - kappa2.unsqueeze(-1) * en_ret - res2.unsqueeze(-1)) >= 0.0
        time_ok = (tnow.unsqueeze(-1).expand(B2, m, n) + T_leg) <= H
        infeasible = infeasible | (is_task & (~served_ok))
        infeasible = infeasible | (is_task & (~load_ok))
        infeasible = infeasible | (is_task & (~en_ok_task))
        infeasible = infeasible | (is_task & (~time_ok))
        # 禁止自环 (j == cur): 原地停留是无意义的占位动作, 且会因 log(T→0) 先验获得高偏置
        self_ok = (curc.unsqueeze(-1) != arN.expand(B2, m, n))
        infeasible = infeasible | (is_task & (~self_ok))
        # 停机坪规则: 仅本机停机坪 & 需要补给 & 不在停机坪 & 能量满足
        need_refill = ((cap_rem < 1.0) | (en_rem < 0.5 * en2)).unsqueeze(-1)
        dep_ok = (depot2.unsqueeze(-1) == arN.expand(B2, m, n)) & need_refill & (curc.unsqueeze(-1) != arN.expand(B2, m, n))
        en_ok_dep = (en_rem.unsqueeze(-1) - en_leg - res2.unsqueeze(-1)) >= 0.0
        infeasible = infeasible | ((~is_task) & (infeasible | (~dep_ok | ~en_ok_dep)))
        if step == 0 and anchor:
            # 真 POMO 锚定: 本条轨迹的第一步固定为 (无人机0, anchor_j) — 其余动作全部屏蔽
            infeasible[arB[:, 0, 0], :, :] = True
            infeasible[arB[:, 0, 0], 0, anchor_j] = False
        # 全部不可行 -> 终止(未服务计入惩罚)
        if infeasible.all():
            break
        logits = policy.logits(h2, curc, cap_rem, en_rem, tnow, infeasible, edge_prior=T_leg / T_scale)
        lsm = F.log_softmax(logits.reshape(B2, -1), dim=-1)
        if anchor and step == 0:
            idx = torch.zeros(B2, dtype=torch.long)
            idx = idx * 0 + (0 * n + anchor_j)   # 强制锚定动作
        elif greedy:
            idx = lsm.argmax(dim=-1)
        else:
            idx = torch.multinomial(lsm.exp(), 1).squeeze(-1)
        logps = logps + lsm.gather(1, idx.unsqueeze(-1)).squeeze(-1)
        for b in range(B2):
            kk = int(idx[b] // n)
            jj = int(idx[b] % n)
            if jj != int(cur[b, kk]):
                leg = float(T2[b, kk, cur[b, kk], jj])
                tnow[b, kk] += leg
                load_now = float(cap_rem[b, kk])
                fac = (float(W2[b, kk] + PKG * load_now) / max(float(W2[b, kk]), 1e-6)) ** 1.5 if use_payload else 1.0
                en_rem[b, kk] = max(0.0, float(en_rem[b, kk]) - leg * fac)
                if jj == int(depot2[b, kk]):
                    cap_rem[b, kk] = cap2[b, kk]
                    en_rem[b, kk] = en2[b, kk]
                    tnow[b, kk] += REFILL
                    actions[b].append((int(kk), jj))    # 停机坪补货
                else:
                    served[b, jj] += 1.0
                    cap_rem[b, kk] -= 1.0
                    tnow[b, kk] += HOVER
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


def make_batch(seed, n_task, B, wind_hours, mode="eastlake", t_service=1.0, drone_w=None,
               kappa=1.0, e_res=0.0, wind_aug=0.0):
    rng = np.random.RandomState(seed)
    batch = []
    for b in range(B):
        if mode == "flow":
            from flow_tasks import build_flow_instance
            inst, _ = build_flow_instance(seed=seed * 997 + b, wind_hour=int(rng.choice(wind_hours)),
                                          n_task=n_task)
        else:
            sc = build_eastlake(seed=seed * 997 + b, n_alerts=n_task, wind_hour=int(rng.choice(wind_hours)))
            inst = build_instance_from_scenario(sc)
        inst.hover_time = t_service            # M1: 校准后的单点作业时间
        if drone_w is not None:
            inst.drone_w = np.array(drone_w, dtype=float)
        inst.kappa = kappa
        inst.energy_reserve = e_res
        if wind_aug > 0.0 and rng.rand() < wind_aug:
            # M2b: 合成强风增强 — 8-12 m/s 随机方向替换风矩阵 (训练分布鲁棒化)
            ang = rng.uniform(0, 2 * np.pi)
            wmag = rng.uniform(8.0, 12.0)
            from scenario import wind_time_matrix
            Tw = wind_time_matrix(inst.xy, drone_speed=15.0, wind=(wmag * np.cos(ang), wmag * np.sin(ang)))
            inst.T = Tw[None].repeat(len(inst.drone_cap), 0) / (np.array([15.0, 15.0, 13.0]) / 15.0)[:, None, None]
        batch.append(inst)
    return batch


def eval_greedy(policy, n_inst=12, n_task=10, seed=12345, mode="eastlake",
                  t_service=1.0, drone_w=None, kappa=1.0, e_res=0.0, wind_aug=0.0):
    batch = make_batch(seed, n_task, n_inst, [0, 12, 36, 100, 200, 300], mode=mode,
                       t_service=t_service, drone_w=drone_w, kappa=kappa, e_res=e_res,
                       wind_aug=wind_aug)
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
    ap.add_argument("--d", type=int, default=128)
    ap.add_argument("--L", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--out", type=str, default="out")
    ap.add_argument("--use-edge", action="store_true", help="ANE-lite 边特征(9维)")
    ap.add_argument("--tanh-prior", action="store_true", help="RRNCO 式解码先验(C·tanh + −β·log T)")
    ap.add_argument("--anchor", action="store_true", help="真 POMO 锚定(各轨迹首任务不同)")
    ap.add_argument("--beta-max", type=float, default=None, help="解码先验 β 上限截断(防先验主导坍缩, 默认不截断)")
    ap.add_argument("--t-service", type=float, default=1.0, help="单点投放作业时间 min (M1, 默认 1.0 校准值)")
    ap.add_argument("--payload-w", default=None, help="逗号分隔空重kg/机 (启用载荷耦合能量 M2, 如 4,4,6)")
    ap.add_argument("--kappa", type=float, default=1.0, help="返航余量系数 κ (M3, 默认 1.0)")
    ap.add_argument("--e-res", type=float, default=0.0, help="绝对能量储备 E_res (min 等效, M3)")
    ap.add_argument("--wind-aug", type=float, default=0.0, help="合成强风增强概率 (M2b: 训练分布注入 8-12 m/s 随机向, 默认 0)")
    ap.add_argument("--mode", default="eastlake", choices=["eastlake", "flow"], help="训练数据模式")
    args = ap.parse_args()
    wlist = ([float(x) for x in args.payload_w.split(",")] if args.payload_w else None)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    cfg = dict(d=args.d, L=args.L, n_feat=(9 if args.use_edge else 6),
               use_edge=args.use_edge, tanh_prior=args.tanh_prior)
    policy = PolicyNetwork(d=args.d, L=args.L, n_feat=cfg["n_feat"],
                           use_edge=args.use_edge, tanh_prior=args.tanh_prior)
    opt = torch.optim.Adam(policy.parameters(), lr=args.lr)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "ckpt_config.json"), "w", encoding="utf-8") as f:
        json.dump(dict(**cfg, steps=args.steps, batch=args.batch, samples=args.samples,
                       n_task=args.n_task, mode=args.mode, anchor=args.anchor, beta_max=args.beta_max), f, indent=1)
    curve = {"step": [], "train_obj": [], "val_obj": []}
    t0 = time.time()
    val_last = None
    for step in range(args.steps):
        batch = make_batch(seed=args.seed * 1000 + step, n_task=args.n_task, B=args.batch,
                           wind_hours=[0, 12, 36, 100, 200, 300, 800, 1400], mode=args.mode,
                           t_service=args.t_service, drone_w=wlist, kappa=args.kappa, e_res=args.e_res,
                           wind_aug=args.wind_aug)
        logps, objs, rts, _ = rollouts(policy, batch, S=args.samples, anchor=args.anchor)
        objs_arr = objs.view(args.batch, args.samples)
        baseline = objs_arr.mean(dim=1, keepdim=True)
        adv = (baseline - objs_arr)                     # 优于基线的轨迹给正优势
        lp = logps.view(args.batch, args.samples)
        loss = -(adv.detach() * lp).mean()
        if args.beta_max is not None and getattr(policy, "prior_beta", None) is not None:
            with torch.no_grad():
                policy.prior_beta.clamp_(0.0, args.beta_max)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        opt.step()
        if step % 50 == 0 or step == args.steps - 1:
            val_obj = eval_greedy(policy, 12, args.n_task, seed=424242, mode=args.mode,
                                 t_service=args.t_service, drone_w=wlist,
                                 kappa=args.kappa, e_res=args.e_res, wind_aug=args.wind_aug)
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
