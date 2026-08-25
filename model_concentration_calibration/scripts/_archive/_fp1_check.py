import json
for f in ['_fp1.json','_fp2.json']:
    try:
        d = json.load(open('D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/'+f, encoding='utf-8'))
        if isinstance(d, list):
            print(f, '->', len(d), 'results')
            for p in d[:6]: print('   ', p.get('name'), p.get('slug'), [ (s.get('ex_max'), s.get('em_max'), s.get('ext_coeff'), s.get('qy'), s.get('maturation')) for s in p.get('states',[])])
        else: print(f, type(d), str(d)[:200])
    except Exception as e: print(f, 'ERR', e)