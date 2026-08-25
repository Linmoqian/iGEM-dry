import json
for f in ['_sf.json','_tr.json']:
    try:
        d = json.load(open('D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/'+f, encoding='utf-8'))
        print(f, '->', d.get('name'), [(s.get('ex_max'), s.get('em_max'), s.get('ext_coeff'), s.get('qy'), s.get('maturation')) for s in d.get('states',[])])
    except Exception as e: print(f, 'ERR', e)