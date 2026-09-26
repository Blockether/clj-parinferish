O_api = ast.literal_eval(OA_api["dirs"]); S_api = ast.literal_eval(SA_api["dirs"])
mods_o = O_api.pop("MODULES"); mods_s = S_api.pop("MODULES")
for k in O_api:
    miss = [x for x in O_api[k] if x not in S_api.get(k,[])]
    extra = [x for x in S_api.get(k,[]) if x not in O_api[k]]
    if miss or extra: print(k, "\n   MISSING:", miss, "\n   EXTRA:", extra)
print("---- modules ----")
for k in mods_o:
    miss = [x for x in mods_o[k] if x not in mods_s.get(k,[])]
    extra = [x for x in mods_s.get(k,[]) if x not in mods_o[k]]
    if miss or extra: print(k, "\n   MISSING:", miss, "\n   EXTRA:", extra)