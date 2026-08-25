import os, re, glob
out = r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/_pdftext'
targets = ['MethyleneBlueAptamer2022_MCLR_electrochemical.txt','MWCNT_FET_MCLR_2024.txt','LabelFreeFET2025_MCLR.txt','ColorimetricAptasensing2024_MCLR.txt','ECL_MCLR_2026_PdMoCu_metallene.txt','CRISPR_Cas12a_colorimetric_MCLR_2023.txt','MatrixEffects2009_MCLR_fluorescent_immunoassay.txt','FPMaturation2022_systematic_invivo_yeast.txt','SmartphoneWCB2020_filter_membrane_water_toxicants.txt','RDX2020_riboswitch_biosensor_modeling_plosone.txt']
pat = re.compile(r'(detection limit|limit of detection|linear range|calibration curve|R\s*[=²]\s*0?\.\d+|LOD|LOQ|[0-9.]+\s*(ng/mL|ng ml|µg/L|ug/L|μg/L|ppb|ppm|nM|pM))', re.I)
for name in targets:
    p = os.path.join(out, name)
    if not os.path.exists(p):
        print('--- missing', name); continue
    txt = open(p, encoding='utf-8').read()
    print('##### ' + name)
    count = 0
    for m in pat.finditer(txt):
        s = max(0, m.start()-70); e = min(len(txt), m.end()+90)
        line = ' '.join(txt[s:e].split())
        print('  *', line[:200])
        count += 1
        if count >= 12: break