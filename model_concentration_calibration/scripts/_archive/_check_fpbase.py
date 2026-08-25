import json
d = json.load(open(r'D:/AAAProject/IGEM/IGEM-dry/model_concentration_calibration/scripts/_fpbase.json', encoding='utf-8'))
print('type:', type(d))
if isinstance(d, dict): print('keys:', list(d.keys())[:10])
prots = d.get('results', d) if isinstance(d, dict) else d
print('n proteins:', len(prots))
for p in prots[:3]: print(json.dumps(p, ensure_ascii=False)[:800])
# find sfGFP and TurboRFP
for p in prots:
    nm = (p.get('name') or '').lower()
    if 'sfgfp' in nm or 'superturborfp' in nm or 'turbo-rfp' in nm or 'turborfp' in nm:
        print('FOUND:', p.get('name'), '| ex:', p.get('ex_max'), '| em:', p.get('em_max'), '| qy:', p.get('qy'), '| ec:', p.get('ec'))