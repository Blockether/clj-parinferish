import re
refs = sorted(set(re.findall(r"`([A-Za-z0-9_./\-]+\.(?:clj|cljs|cljc|md|edn|tsx|ts|py|mjs|json|version|sdkmanrc))`", txt)))
def find(p):
    q = root/p
    if q.exists(): return "OK  "+p
    # search by basename
    hits = glob.glob(str(root/"**"/os.path.basename(p)), recursive=True)
    return f"?? {p} -> {[h.replace(str(root)+'/','') for h in hits[:3]]}"
for p in refs: print(find(p))
print("---- root tree ----")
print(ls(str(root), depth=1))