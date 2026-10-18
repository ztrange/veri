import json,sys,re
# parse.py <run.json> <req-file> -> prints "PASS|REJECT|NOVERDICT <fails>"; strict
res=json.load(open(sys.argv[1]))['result']
ids=[l.split('|')[0].strip() for l in open(sys.argv[2]) if l.strip()]
m=re.findall(r'BEGIN GRADES\n(.*?)\nEND GRADES', res, re.S)
if len(m)!=1 or not res.rstrip().endswith('END GRADES'): print('NOVERDICT block'); sys.exit(2)
lines=m[0].strip().split('\n')
grades=[re.match(r'^([A-Z]+[0-9]+): (PASS|FAIL) — ',l) for l in lines[:-1]]
if any(g is None for g in grades) or [g[1] for g in grades]!=ids: print('NOVERDICT lines'); sys.exit(2)
v=re.fullmatch(r'VERDICT: (PASS|REJECT)',lines[-1].strip())
fails=[g[1] for g in grades if g[2]=='FAIL']
derived='REJECT' if fails else 'PASS'
if not v or v[1]!=derived: print('NOVERDICT mismatch'); sys.exit(2)
print(derived,' '.join(fails)); sys.exit(0 if derived=='PASS' else 1)
