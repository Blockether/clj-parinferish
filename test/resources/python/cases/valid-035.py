import ast
old_src = ntr["call_Yz1yL25HKfJqXBFqa3jjImbF|fc_022ea9c3af40e84b016a6e5106ca188191834a3d38caceec31"]["commands"][0]["stdout"]
cat_r = ntr["call_05M2bknwVKzEkxirS0eRq6Nb|fc_022ea9c3af40e84b016a6e50f508f481919ba5c77c1e343e3d"]["results"][0]["anchors"]
current_region = "\n".join(v["text"] for k,v in sorted(cat_r.items(), key=lambda kv:int(kv[0].split(':')[0])))

def strings(src):
    tree=ast.parse(src)
    out={}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value,str):
            target=node.targets[0]
            if isinstance(target, ast.Attribute) and target.attr=='__doc__':
                out[target.value.id+'.__doc__']=node.value.value
            elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id=='docs':
                key=ast.literal_eval(target.slice)
                out['docs.'+key]=node.value.value
    return out
old = strings(old_src)
cur = strings("def _():\n"+current_region)
for name in old:
    if name in cur:
        print(f"{name}: {len(old[name])} -> {len(cur[name])} ({(len(cur[name])/len(old[name])-1)*100:.1f}%)")
for prefix in ('docs.',''):
    names=[k for k in old if k.startswith(prefix) and (prefix or '__doc__' in k)]
    if names:
        a=sum(len(old[k]) for k in names); b=sum(len(cur[k]) for k in names)
        print(f"{prefix or '__doc__'} total: {a} -> {b} ({(b/a-1)*100:.1f}%)")