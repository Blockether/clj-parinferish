root = Path(session["workspace"]["root"])
r = await gather(
    read_session(),
    grep({"query": ["server switcher", "machine switcher", "live", "idle", "active", "inactive", "health"], "paths": [str(root / "apps/vis-companion/src"), str(root / "src/com/blockether/vis/internal/gateway")]})
print(r[1])