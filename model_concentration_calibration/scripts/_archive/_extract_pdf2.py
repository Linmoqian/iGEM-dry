import os, glob
from pypdf import PdfReader
ref = r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/references'
out = r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/_pdftext'
os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob(ref + '/*.pdf')):
    name = os.path.basename(f).replace('.pdf','')
    dst = os.path.join(out, name + '.txt')
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        print('skip', name); continue
    try:
        rd = PdfReader(f)
        pages = [p.extract_text() or '' for p in rd.pages]
        txt = '\n\n===PAGE===\n\n'.join(pages)
        open(dst, 'w', encoding='utf-8').write(txt)
        print(f'{name}: {len(rd.pages)} pages, {len(txt)} chars')
    except Exception as e:
        print(f'{name}: ERR {e}')