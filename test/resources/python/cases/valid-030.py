cur = Path(lp).read_text().split("\n")
def find(pred, start=0):
    for i in range(start, len(cur)):
        if pred(cur[i]): return i
    return -1

h0 = find(lambda l: l.startswith("(defn- envelope-with-settled-views"))
h1 = find(lambda l: l.startswith("(defn- run-python-code"), h0)
s0 = find(lambda l: l.strip().startswith(";; The close lands HERE"), h1)
s1 = find(lambda l: l.strip() == "exec-future", s0)
t0 = find(lambda l: l.strip().startswith("(let [swept"), s1)
e0 = find(lambda l: l.strip().startswith("(let [;; A cancel unwinds"), t0)
e1 = find(lambda l: l.startswith("(defn- run-with-timing"), e0)
print(h0,h1,s0,s1,t0,e0,e1)
print("--- helper tail ---"); print("\n".join(cur[h1-3:h1+1]))
print("--- sweep head ---"); print("\n".join(cur[s0-4:s0+2]))
print("--- sweep tail/exec ---"); print("\n".join(cur[s1-4:s1+1]))
print("--- timeout head ---"); print("\n".join(cur[t0-4:t0+2]))
print("--- error/end ---"); print("\n".join(cur[e0-2:e0+2])); print("...")
print("\n".join(cur[e1-4:e1+1]))
