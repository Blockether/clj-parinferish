root = Path(session["workspace"]["root"])
prov = root/"src/com/blockether/vis/internal/provider"
tprov = root/"test/com/blockether/vis/internal/provider"
S = {}
for d in ("openai_codex", "opencode_go"):
    S[d] = dict(
        lim=(prov/d/"limits.clj").read_text(),
        main=(prov/f"{d}.clj").read_text(),
        tlim=(tprov/d/"limits_test.clj").read_text(),
        tmain=(tprov/f"{d}_test.clj").read_text(),
    )

def ns_form(src):
    """Return (ns_text, rest) splitting a clj source at the end of its top-level ns form."""
    i = src.index("(ns ")
    depth, j, in_str, esc = 0, i, False, False
    while j < len(src):
        c = src[j]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        elif c == '"': in_str = True
        elif c == ";":
            j = src.index("\n", j)
        elif c == "(": depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return src[i:j+1], src[j+1:]
        j += 1
    raise ValueError("unbalanced ns")

def defs(src):
    return re.findall(r"^\((?:defn?-?|defonce|defmacro|defmulti|defmethod|defrecord|defprotocol|deftest|defdescribe) \^?[:\w\-]*\s*([\w\-!?*>.<=]+)", src, re.M)

for d, v in S.items():
    print(f"\n######## {d}")
    for k in ("lim", "main", "tlim", "tmain"):
        ns, body = ns_form(v[k])
        print(f"--- {k} ns form:\n{ns}")
        print(f"{k} defs:", defs(body))
    lim_defs, main_defs = set(defs(S[d]["lim"])), set(defs(S[d]["main"]))
    print("COLLISIONS src:", lim_defs & main_defs)
    print("COLLISIONS test:", set(defs(S[d]["tlim"])) & set(defs(S[d]["tmain"])))
    alias = {"openai_codex": "codex-limits", "opencode_go": "go-limits"}[d]
    uses = re.findall(rf"{alias}/([\w\-!?*>]+)", S[d]["main"])
    print("main uses of limits alias:", Counter(uses))
    print("tmain uses of limits alias:", Counter(re.findall(rf"{alias}/([\w\-!?*>]+)", S[d]["tmain"])))
    # first consumer top-level form line
    m = re.search(rf"^\((?:defn?-?|def|defonce).*?(?=^\(|\Z)", S[d]["main"], re.M | re.S)
    lines = S[d]["main"].splitlines()
    first = next((i for i, l in enumerate(lines) if f"{alias}/" in l and not l.lstrip().startswith("[")), None)
    print("first alias use at line", first + 1 if first is not None else None)
    tl_aliases = re.findall(r"\[([\w\.\-]+) :as ([\w\-]+)\]", ns_form(S[d]["tlim"])[0])
    print("tlim aliases:", tl_aliases)
    print("tlim alias uses:", Counter(re.findall(r"(?<![\w\-])([\w\-]+)/[\w\-!?*>]+", ns_form(S[d]["tlim"])[1])))
    print("tlim context/fixtures:", re.findall(r"set-ns-context!|around-each|before|after", S[d]["tlim"]))
    print("tmain context/fixtures:", re.findall(r"set-ns-context!|around-each", S[d]["tmain"]))

extra = grep({"query": ["codex.limits", "opencode_go.limits", "opencode-go.limits", "limits_test", "openai_codex/limits", "opencode_go/limits"], "paths": [str(root/"resources"), str(root/"test-native"), str(root/"e2e"), str(root/"scripts"), str(root/"build.clj"), str(root/".github"), str(root/"apps/vis-tui"), str(root/"AGENTS.md"), str(root/"PLAN.md"), str(root/"CHANGELOG.md")], "context": 0})
print(extra)