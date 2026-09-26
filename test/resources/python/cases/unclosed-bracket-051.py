root = Path(session["workspace"]["root"])
rs, hits = await gather(
    read_session(),
    grep({"query": ["def _elapsed", "startedAt", "active_step_ids", "run_shape"], "paths": [str(root / ".vis/extensions/gh.py"), str(root / ".vis/extensions/test_gh.py")]})
print(hits)
print({"session_id": rs.get("id") if isinstance(rs, dict) else None, "turns": len(rs.get("transcript", {}).get("turns", [])) if isinstance(rs, dict) else None})