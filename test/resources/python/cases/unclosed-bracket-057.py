root = Path(session["workspace"]["root"])
rs, hits = await gather(
    read_session(),
    grep({"query": ["cancelled", "canceled", "conclusion", "while True", "def watch", "superseded"], "paths": [str(root / ".vis/extensions/gh.py"), str(root / ".vis/extensions/test_gh.py")]})
print(hits)