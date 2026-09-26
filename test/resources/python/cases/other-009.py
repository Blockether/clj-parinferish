import json as _json

def iter_code_blocks(paths):
    """Yield (file, code_string) for every python_execution code payload found."""
    for p in paths:
        try:
            with open(p, "r", errors="replace") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if not ln or '"code"' not in ln:
                        continue
                    try:
                        obj = _json.loads(ln)
                    except Exception:
                        continue
                    stack = [obj]
                    while stack:
                        o = stack.pop()
                        if isinstance(o, dict):
                            c = o.get("code")
                            if isinstance(c, str) and len(c) > 0:
                                yield p.name, c
                            stack.extend(v for v in o.values() if isinstance(v, (dict, list)))
                        elif isinstance(o, list):
                            stack.extend(v for v in o if isinstance(v, (dict, list)))

recent = files[:40]
blocks = list(iter_code_blocks(recent))
print("code blocks:", len(blocks), "from", len(recent), "journals")
