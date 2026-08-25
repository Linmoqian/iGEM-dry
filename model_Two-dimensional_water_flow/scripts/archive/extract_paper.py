# -*- coding: utf-8 -*-
import os, re
from pypdf import PdfReader
p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\report\references\ijgi-09-00094.pdf'
r = PdfReader(p)
print('pages:', len(r.pages))
text = []
for pg in r.pages:
    t = pg.extract_text() or ''
    text.append(t)
full = '\\n'.join(text)
out = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\report\references\ijgi-09-00094_extracted.txt'
open(out, 'w', encoding='utf-8').write(full)
print('chars:', len(full))
print(full[:2500])
