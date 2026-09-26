root = Path(session["workspace"]["root"])
app = root / "apps" / "vis-companion"
rs, hits = await gather(
    read_session(),
    grep({"query": ["Engine default", "Pocket TTS", "favorite", "favourite", "idle", "Star", "star"],
          "paths": [app / "src"]})
print("session", rs.get("id") if isinstance(rs, dict) else type(rs).__name__)
print(hits[:24000] if isinstance(hits, str) else hits)