gl = Path.home()/".vis/logs/gateway-20260903T091105Z-pid38882.log"
raw = gl.read_text(errors="replace")
L = raw.splitlines()
print(len(L))
idx=[i for i,l in enumerate(L) if l.startswith("2026-09-03T14:5")]
print("14:5x lines:", len(idx), L[idx[0]][:120] if idx else None)
win=[i for i in idx if l4 := True]
sel=[i for i in idx if L[i][:19] >= "2026-09-03T14:50:50" and L[i][:19] <= "2026-09-03T14:51:40"]
print("window:", len(sel))
for i in sel:
    print(L[i][:400])
