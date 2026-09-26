_cat_cache.clear()
txt = Path(core).read_text().splitlines()
def find(pat, start=1):
    for i,l in enumerate(txt,1):
        if i>=start and pat in l: return i
    raise LookupError(pat)
for pat in ["(defmacro ^:private and-merge", "(defn- eval-ctx", "(defn compile", "{:skjema/compiled true", "(defn validate", "(defn- eval-schema", "and-merge ctx"]:
    print(pat, "->", [i for i,l in enumerate(txt,1) if pat in l][:20])