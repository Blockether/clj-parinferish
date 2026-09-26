> 
hits = []
for p in list((root/".github").rglob("*.yml")) + list((root/"scripts").rglob("*")) + [root/"e2e/run.py", root/"AGENTS.md", root/"README.md"]:
    if p.is_file():
        try: t = p.read_text()
        except Exception: continue
        for i, l in enumerate(t.splitlines(), 1):
            if re.search(r"\bbun\b|\bBun\b|typescript", l, re.I) and "ubuntu" not in l.lower() and "bundle" not in l.lower():
                hits.append(f"{p.relative_to(root)}:{i}: {l.strip()[:120]}")
print("\n".join(hits) or "none")