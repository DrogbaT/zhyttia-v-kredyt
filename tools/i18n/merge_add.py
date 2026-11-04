"""Merge add_*.txt (lang|idx§text) for keys in add_keys.txt into tr_<lang>.json, with the same checks as check.py."""
import re,json,sys
keys={}
for line in open('add_keys.txt',encoding='utf-8').read().split('\n'):
    if line:i,k=line.split('\t',1);keys[int(i)]=k
ph=lambda s:sorted(re.findall(r'\{\d+\}',s));tags=lambda s:re.findall(r'</?[a-z]+[^>]*>',s)
ws=lambda s:(len(s)-len(s.lstrip(' ')),len(s)-len(s.rstrip(' ')))
by={}
for line in open(sys.argv[1],encoding='utf-8').read().split('\n'):
    if '§' not in line:continue
    head,t=line.split('§',1);lang,i=head.split('|');by.setdefault(lang,{})[int(i)]=t
errs=0
for lang,tr in by.items():
    d=json.load(open(f'tr_{lang}.json',encoding='utf-8'))
    for i,k in keys.items():
        if i not in tr:print(lang,'missing',i);errs+=1;continue
        l,r=ws(k);t=' '*l+tr[i].strip(' ')+' '*r
        if ph(k)!=ph(t) or tags(k)!=tags(t):print(lang,i,'mismatch',ph(k),ph(t),tags(k),tags(t));errs+=1;continue
        d[k]=t
    json.dump(d,open(f'tr_{lang}.json','w',encoding='utf-8'),ensure_ascii=False)
print('langs',sorted(by),'errors',errs)
