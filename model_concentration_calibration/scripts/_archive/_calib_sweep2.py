import os, re
out = r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/_pdftext'
targets = ['MethyleneBlueAptamer2022_MCLR_electrochemical.txt','MWCNT_FET_MCLR_2024.txt','LabelFreeFET2025_MCLR.txt','ColorimetricAptasensing2024_MCLR.txt','ECL_MCLR_2026_PdMoCu_metallene.txt','CRISPR_Cas12a_colorimetric_MCLR_2023.txt','MatrixEffects2009_MCLR_fluorescent_immunoassay.txt','SmartphoneWCB2020_filter_membrane_water_toxicants.txt']
pat = re.compile(r'(detection limit|limit of detection|linear range|calibration curve|LOD|LOQ)', re.I)
for name in targets:
    p = os.path.join(out, name)
    if not os.path.exists(p):
        print('--- missing', name); continue
    lines = open(p, encoding='utf-8').read().splitlines()
    print('##### ' + name)
    hits = [i for i, L in enumerate(lines) if pat.search(L)]
    for i in hits[:10]:
        seg = ' '.join(x.strip() for x in lines[max(0,i-1):i+2] if x.strip())
        print('  *', seg[:210])