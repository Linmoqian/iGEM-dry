# -*- coding: utf-8 -*-
"""
model.py — 任务级路径规划策略网络 (v1.4 定稿)
架构: [节点特征] -> 输入投影 + 类型嵌入 -> Transformer 编码器(L=3,d=128,H=8,MFF=512)
      -> 多智能体指针解码器 (每步联合选 (无人机k, 目标j))
      -> 约束掩码(容量/能量+返航余量/时间窗/需求/停机坪归属)
注: 能量掩码强制 "任意时刻可返航", 保证生成解在 env.simulate 中 feasible。
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    def __init__(self, d, H):
        super().__init__()
        self.d, self.H = d, H
        self.Wq = nn.Linear(d, d); self.Wk = nn.Linear(d, d)
        self.Wv = nn.Linear(d, d); self.Wo = nn.Linear(d, d)
        self.scale = d ** -0.5

    def forward(self, q, k, v, mask=None):
        B, qn, _ = q.shape
        Q = self.Wq(q).view(B, qn, self.H, self.d // self.H).transpose(1, 2)
        K = self.Wk(k).view(B, k.shape[1], self.H, self.d // self.H).transpose(1, 2)
        V = self.Wv(v).view(B, k.shape[1], self.H, self.d // self.H).transpose(1, 2)
        att = Q @ K.transpose(-2, -1) * self.scale
        if mask is not None:
            att = att.masked_fill(mask, -1e9)
        att = F.softmax(att, dim=-1)
        out = (att @ V).transpose(1, 2).reshape(B, qn, self.d)
        return self.Wo(out)


class EncoderLayer(nn.Module):
    def __init__(self, d=128, H=8, ff=512):
        super().__init__()
        self.attn = MultiHeadAttention(d, H)
        self.norm1 = nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Linear(d, ff), nn.ReLU(), nn.Linear(ff, d))
        self.norm2 = nn.LayerNorm(d)

    def forward(self, x):
        h = self.norm1(x + self.attn(x, x, x))
        return self.norm2(h + self.ff(h))


class PolicyNetwork(nn.Module):
    def __init__(self, d=128, H=8, L=3, ff=512, n_feat=6, use_edge=False, tanh_prior=False):
        super().__init__()
        self.d = d
        self.use_edge = use_edge
        self.tanh_prior = tanh_prior
        self.input_proj = nn.Linear(n_feat, d)
        self.enc_layers = nn.ModuleList([EncoderLayer(d, H, ff) for _ in range(L)])
        self.node_type = nn.Embedding(2, d)
        self.ctx_proj = nn.Linear(d + 3, d)
        self.q_proj = nn.Linear(d, d)
        self.scale = d ** -0.5
        if tanh_prior:
            # RRNCO 式解码先验: C·tanh(·) 截断 + 负对数距离(成本) 偏置; β 可学习, 初值 1
            self.prior_beta = nn.Parameter(torch.tensor(1.0))
            self.tanh_C = 10.0

    def encode(self, x, is_depot):
        h = self.input_proj(x) + self.node_type(is_depot.long())
        for layer in self.enc_layers:
            h = layer(h)
        return h

    def logits(self, h, cur, cap_rem, en_rem, time_now, infeasible, edge_prior=None):
        """h:(B,n,d) cur:(B,m) cap_rem/en_rem/time_now:(B,m) -> logits:(B,m,n); infeasible:(B,m,n) bool
        edge_prior: (B,m,n) 归一化边成本 T_leg/scale; tanh_prior=True 时按 RRNCO 式21 加 tanh 截断与 −β·log(cost) 先验。
        """
        B, m = cur.shape
        n = h.shape[1]
        h_bar = h.mean(dim=1, keepdim=True).expand(B, m, self.d)
        last = torch.gather(h, 1, cur.unsqueeze(-1).expand(B, m, self.d))
        dyn = torch.stack([cap_rem, en_rem, time_now], dim=-1)  # (B,m,3)
        ctx = self.ctx_proj(torch.cat([h_bar + last, dyn], dim=-1))
        q = self.q_proj(ctx)
        logits = (q @ h.transpose(-2, -1)) * self.scale
        if self.tanh_prior:
            logits = self.tanh_C * torch.tanh(logits)
            if edge_prior is not None:
                logits = logits - self.prior_beta * torch.log(edge_prior + 1e-6)
        logits = logits.masked_fill(infeasible, -1e9)
        return logits

    def forward(self, x, is_depot):
        return self.encode(x, is_depot)
