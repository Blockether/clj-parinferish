root = Path(session["workspace"]["root"])
spel_root = Path('/home/user/spel')
rs, hits = await gather(
    read_session(),
    grep({"query": ["release", "VERSION", "Clojars", "git tag", "deploy"], "paths": [str(spel_root / "AGENTS.md"), str(spel_root / "Makefile"), str(spel_root / ".github"), str(spel_root / "README.md"), str(spel_root / "deps.edn")]})
print(hits[:18000])