"""Validate a translation file (lines: index<TAB>text) against keys.txt.
Checks: every index present once, same {n} placeholders, same HTML tags in order,
same leading/trailing spaces. Writes tr_<lang>.json (ukrainian key -> text)."""
import re,sys,json
D='/tmp/claude-0/-home-claude/bde9d0ca-e67a-5d0b-b818-56313b6c165b/scratchpad/i18n/'
keys={}
for line in open(D+'keys.txt',encoding='utf-8').read().split('\n'):
    i,k=line.split('\t',1);keys[int(i)]=k.replace('\\n','\n')
lang=sys.argv[1]
tr={};errs=[]
raw=open(D+f'{lang}.txt',encoding='utf-8').read().split('\n')
for line in raw:
    if not line.strip() or '§' not in line:continue
    i,t=line.split('§',1);i=int(i)
    if i in tr:errs.append(f'dup {i}')
    tr[i]=t
ph=lambda s:sorted(re.findall(r'\{\d+\}',s))
tags=lambda s:re.findall(r'</?[a-z]+[^>]*>',s)
def ws(s):return (len(s)-len(s.lstrip(' ')),len(s)-len(s.rstrip(' ')))
for i,k in keys.items():
    if i not in tr:errs.append(f'missing {i}: {k[:50]}');continue
    l,r=ws(k);t=' '*l+tr[i].strip(' ')+' '*r;tr[i]=t
    if ph(k)!=ph(t):errs.append(f'placeholders {i}: {k[:40]} | {t[:40]}')
    if tags(k)!=tags(t):errs.append(f'tags {i}: {tags(k)} | {tags(t)}')
    if ws(k)!=ws(t):errs.append(f'spaces {i}: {k!r} | {t!r}')
for e in errs[:40]:print(e)
print(lang,'ok' if not errs else f'{len(errs)} errors',len(tr),'/',len(keys))
if not errs:json.dump({keys[i]:tr[i] for i in keys},open(D+f'tr_{lang}.json','w',encoding='utf-8'),ensure_ascii=False)
