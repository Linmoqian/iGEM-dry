# -*- coding: utf-8 -*-
"""Lake Erie 2018-2019 毒素谱统计：MC-LR/总MC 比例、胞内/胞外池比例。"""
import pandas as pd, numpy as np, os
import sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'data', 'raw', 'Lake Erie', 'waterqualitysamplingdata2018-2019habs.xlsx')
d = pd.read_excel(p, sheet_name='HABs Grab all')
tc = [c for c in d.columns if 'Microcystins' in str(c) and 'ELISA' in str(c) and 'Total' in str(c)][0]
ec = [c for c in d.columns if 'Extracellular' in str(c)][0]
mclr_c = [c for c in d.columns if 'MC-LR' in str(c)][0]
total = pd.to_numeric(d[tc], errors='coerce'); extra = pd.to_numeric(d[ec], errors='coerce'); mclr = pd.to_numeric(d[mclr_c], errors='coerce')/1000.0
ok = total.notna() & mclr.notna() & (total > 0)
ratio = mclr[ok]/total[ok]
ok2 = total.notna() & extra.notna() & (total > 0)
frac_extra = extra[ok2]/total[ok2]
print('MC-LR/total: n=%d median=%.3f IQR=%.3f-%.3f P90=%.3f' % (ok.sum(), np.nanmedian(ratio), *np.nanpercentile(ratio,[25,75]), np.nanpercentile(ratio,90)))
print('total MC pct: ', np.round(np.nanpercentile(total[total>0],[50,75,90,95,99]),3))
print('MC-LR ug/L pct: ', np.round(np.nanpercentile(mclr[mclr>0],[50,75,90,95,99]),3))
print('extracellular fraction: median=%.3f IQR=%.3f-%.3f P90=%.3f -> intracellular median=%.3f' % (np.nanmedian(frac_extra), *np.nanpercentile(frac_extra,[25,75]), np.nanpercentile(frac_extra,90), 1-np.nanmedian(frac_extra)))