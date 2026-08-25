# -*- coding: utf-8 -*-
"""Mendeley 数据集提取（修正版）"""
import os, math
import openpyxl
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw', 'Mendeley Data_Filterable bacterioplankton able to degrade microcystin', 'submit results data.xlsx')
PROC = os.path.join(ROOT, 'data', 'processed')
os.makedirs(PROC, exist_ok=True)

wb = openpyxl.load_workbook(RAW, read_only=True, data_only=True)
ws = wb['MC-LR raw data_submit ']
rows = list(ws.iter_rows(values_only=True))

blocks = []
for i, r in enumerate(rows):
    v = r[0] if r else None
    if hasattr(v, 'year'):
        blocks.append(i)
blocks.append(len(rows))

GROUP_COLS = {
    'autoclaved': {'raw': [2, 4], 'pct': [6, 7]},
    'frac<0.025um': {'raw': [10, 11, 12, 13], 'pct': [14, 15]},
    'frac<0.22um': {'raw': [18, 19, 20, 21], 'pct': [22, 23]},
    'frac<0.45um': {'raw': [26, 27, 28, 29], 'pct': [30, 31]},
}

records = []
for b in range(len(blocks) - 1):
    hdr_i = blocks[b]
    mean_i = hdr_i + 4  # date+labels, rep1, rep2, rep3, mean, SD
    if mean_i >= blocks[b + 1]:
        continue
    date = rows[hdr_i][0]
    hdr_raw = rows[hdr_i]
    labels = {}
    for g, cfg in GROUP_COLS.items():
        for ci in cfg['raw']:
            lab = hdr_raw[ci] if ci < len(hdr_raw) else None
            lab = str(lab).strip() if lab is not None else ''
            if lab.upper().startswith('T'):
                labels[('raw', g, ci)] = lab
        for ci in cfg['pct']:
            lab = hdr_raw[ci] if ci < len(hdr_raw) else None
            lab = str(lab).strip() if lab is not None else ''
            if lab.upper().startswith('T'):
                labels[('pct', g, ci)] = lab
    mean_row = rows[mean_i]
    if mean_row is None:
        continue
    for (kind, g, ci), lab in labels.items():
        val = mean_row[ci] if ci < len(mean_row) else None
        if val is None or isinstance(val, str):
            continue
        try:
            v = float(val)
        except Exception:
            continue
        if kind == 'raw':
            records.append({'date': str(date.date()), 'treatment': g, 'timepoint': lab, 'MC_LR_ng_mL': v})
        else:
            records.append({'date': str(date.date()), 'treatment': g, 'timepoint': 'pct__' + lab, 'remaining_fraction': v})

df = pd.DataFrame(records)
raw = df[df['MC_LR_ng_mL'].notna()].copy()
raw = raw.sort_values(['treatment', 'date', 'timepoint'])
raw.to_csv(os.path.join(PROC, 'Mendeley_filterable_MCLR_time_series.csv'), index=False)
print(raw.to_string(index=False))
print()
ks = []
for (date, treat), sub in raw.groupby(['date', 'treatment']):
    t0 = sub[sub['timepoint'] == 'T0']['MC_LR_ng_mL']
    t7 = sub[sub['timepoint'] == 'T7']['MC_LR_ng_mL']
    if len(t0) == 0 or len(t7) == 0:
        continue
    c0 = float(t0.iloc[0]); c7 = float(t7.iloc[0])
    if c0 <= 0:
        continue
    if c7 >= c0:
        k = 0.0; censored = False
    else:
        k = -math.log(c7 / c0) / 7.0
        censored = (c7 <= 0.11)
    ks.append({'date': date, 'treatment': treat, 'C0_ng_mL': round(c0, 4), 'C7_ng_mL': round(c7, 4),
               'remaining_frac_T7': round(c7 / c0, 4), 'k_d-1': round(k, 4), 'censored_LOD': censored})
kdf = pd.DataFrame(ks)
kdf.to_csv(os.path.join(PROC, 'Mendeley_MCLR_apparent_k_estimates.csv'), index=False)
print(kdf.to_string(index=False))
