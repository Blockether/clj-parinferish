print("diagnosis",json.dumps(rs.get('diagnosis'),ensure_ascii=False,default=str)[:12000])
print("turn_retries",json.dumps(rs.get('turn_retries'),ensure_ascii=False,default=str)[:12000])
usage=rs.get('usage',{})
print("usage keys",list(usage.keys()))
# recursively find dicts with iteration 66 or status 500, compact
def find(obj,path=()):
    out=[]
    if isinstance(obj,dict):
        if obj.get('iteration')==66 or obj.get('status')==500 or obj.get('provider_status')==500:
            out.append((path,obj))
        for k,v in obj.items(): out.extend(find(v,path+(str(k),)))
    elif isinstance(obj,list):
        for i,v in enumerate(obj): out.extend(find(v,path+(str(i),)))
    return out
found=find(usage)
print("found",len(found))
for p,o in found[:30]: print('/'.join(p),json.dumps(o,ensure_ascii=False,default=str)[:5000])