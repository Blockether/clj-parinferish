spel_root = Path('/home/user/spel')
rs, release_hits = await gather(
    read_session(),
    grep({"query": ["Release", "SPEL_VERSION", "version bump", "Clojars", "workflow_dispatch", "tags:"], "paths": [str(spel_root / "AGENTS.md"), str(spel_root / ".github/workflows/release.yml"), str(spel_root / "Makefile"), str(spel_root / "README.md")]})
print(release_hits)
print({"session_id": rs.get("id") if isinstance(rs, dict) else None, "session_keys": list(rs)[:12] if isinstance(rs, dict) else type(rs).__name__})