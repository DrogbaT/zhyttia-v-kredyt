"""Wrap every Ukrainian text run in the game script with T(...) so it can be translated.
- plain '..' / ".." strings with Cyrillic  -> T('..')
- template literals: text runs between HTML tags (and quoted attribute values) that
  contain Cyrillic become ${T(`run with {0},{1} placeholders`, expr0, expr1)}
Keys collected to keys.json."""
import re,json,sys
CYR=re.compile(r'[А-Яа-яЇїІіЄєҐґ’]')
src=open(sys.argv[1],encoding='utf-8').read()
keys={}
def addkey(k):
    keys[k]=keys.get(k,0)+1
def js_str(k):
    return json.dumps(k,ensure_ascii=False)

class P:
    def __init__(s,t):s.t=t;s.i=0
def parse_code(p,end_on_brace=False):
    """parse JS code until end (or unmatched '}' if end_on_brace); return transformed code"""
    out=[];t=p.t;depth=0
    while p.i<len(t):
        c=t[p.i]
        if c in '\'"':
            j=p.i+1
            while t[j]!=c:
                if t[j]=='\\':j+=1
                j+=1
            lit=t[p.i:j+1];p.i=j+1
            body=lit[1:-1]
            if CYR.search(body) and not prev_is_T(out):
                val=json.loads('"'+body.replace('\\\'',"'").replace('"','\\"')+'"') if c=="'" else json.loads(lit)
                addkey(val);out.append('T('+js_str(val)+')')
            else:out.append(lit)
            continue
        if c=='`':
            p.i+=1;out.append(parse_template(p));continue
        if c=='/' and t[p.i+1]=='/':
            j=t.index('\n',p.i);out.append(t[p.i:j]);p.i=j;continue
        if c=='/' and t[p.i+1]=='*':
            j=t.index('*/',p.i)+2;out.append(t[p.i:j]);p.i=j;continue
        if c=='/' and regex_ok(out):
            # regex literal
            j=p.i+1;cls=False
            while True:
                ch=t[j]
                if ch=='\\':j+=2;continue
                if ch=='[':cls=True
                elif ch==']':cls=False
                elif ch=='/' and not cls:break
                j+=1
            j+=1
            while j<len(t) and t[j].isalpha():j+=1
            out.append(t[p.i:j]);p.i=j;continue
        if c=='{':depth+=1
        if c=='}':
            if depth==0 and end_on_brace:
                p.i+=1;return ''.join(out)
            depth-=1
        out.append(c);p.i+=1
    return ''.join(out)
def prev_is_T(out):
    s=''.join(out[-3:])
    return s.endswith('T(')
def regex_ok(out):
    s=''.join(out[-20:]).rstrip()
    return (not s) or s[-1] in '(,=:[!&|?{};+-*%<>~^' or s.endswith('return')
def parse_template(p):
    """p.i just after opening backtick. returns transformed template literal incl. backticks"""
    t=p.t;parts=[]  # list of ('s',text) or ('e',code)
    buf=''
    while True:
        c=t[p.i]
        if c=='\\':buf+=t[p.i:p.i+2];p.i+=2;continue
        if c=='`':p.i+=1;break
        if c=='$' and t[p.i+1]=='{':
            parts.append(('s',buf));buf='';p.i+=2
            parts.append(('e',parse_code(p,True)));continue
        buf+=c;p.i+=1
    parts.append(('s',buf))
    return '`'+segment(parts)+'`'
def segment(parts):
    """rebuild template body; wrap text runs (outside tags) containing Cyrillic"""
    # flatten into tokens: chars of static text, or expr markers
    toks=[]
    for k,v in parts:
        if k=='s':toks+=[('c',ch) for ch in v]
        else:toks.append(('e',v))
    out=[];i=0;n=len(toks)
    def flush_run(run):
        # run: list of tokens forming visible text; trim whitespace edges
        if not run:return ''
        stat=''.join(v for k,v in run if k=='c')
        if not CYR.search(stat):
            return ''.join(v if k=='c' else '${'+v+'}' for k,v in run)
        # leading/trailing whitespace stays outside
        l=0
        while l<len(run) and run[l][0]=='c' and run[l][1].isspace():l+=1
        r=len(run)
        while r>l and run[r-1][0]=='c' and run[r-1][1].isspace():r-=1
        core=run[l:r];key='';args=[]
        for k,v in core:
            if k=='c':key+=v
            else:key+='{'+str(len(args))+'}';args.append(v)
        key=key.replace('\\`','`').replace('\\$','$')
        addkey(key)
        lead=''.join(v for k,v in run[:l]);trail=''.join(v for k,v in run[r:])
        return lead+'${T('+js_str(key)+(''.join(','+a for a in args))+')}'+trail
    run=[]
    while i<n:
        k,v=toks[i]
        if k=='c' and v=='<':
            # inline formatting tags stay inside the sentence
            j=i;tg=''
            while j<n and toks[j][0]=='c' and toks[j][1]!='>' and len(tg)<12:tg+=toks[j][1];j+=1
            if j<n and toks[j]==('c','>') and re.fullmatch(r'</?(b|em|small|strong)',tg):
                run+=toks[i:j+1];i=j+1;continue
            out.append(flush_run(run));run=[]
            # copy tag; translate quoted attr values with cyrillic
            tag=[];j=i
            while j<n and not (toks[j]==('c','>')):
                tag.append(toks[j]);j+=1
            if j<n:tag.append(toks[j]);j+=1
            out.append(tag_text(tag));i=j;continue
        run.append(toks[i]);i+=1
    out.append(flush_run(run))
    return ''.join(out)
def tag_text(tag):
    out=[];i=0;n=len(tag)
    while i<n:
        k,v=tag[i]
        if k=='c' and v=='"':
            j=i+1;val=[]
            while j<n and tag[j]!=('c','"'):val.append(tag[j]);j+=1
            stat=''.join(x for kk,x in val if kk=='c')
            if CYR.search(stat):
                key='';args=[]
                for kk,x in val:
                    if kk=='c':key+=x
                    else:key+='{'+str(len(args))+'}';args.append(x)
                addkey(key)
                out.append('"${T('+js_str(key)+''.join(','+a for a in args)+')}"')
            else:out.append('"'+''.join(x if kk=='c' else '${'+x+'}' for kk,x in val)+'"')
            i=j+1;continue
        out.append(v if k=='c' else '${'+v+'}');i+=1
    return ''.join(out)

html=src
m=list(re.finditer(r'<script>(.*?)</script>',html,re.S))[-1]
code=m.group(1)
p=P(code);newcode=parse_code(p)
newhtml=html[:m.start(1)]+newcode+html[m.end(1):]
open(sys.argv[2],'w',encoding='utf-8').write(newhtml)
json.dump(keys,open(sys.argv[3],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('keys',len(keys),'chars',sum(len(k) for k in keys))
