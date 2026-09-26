root = Path(session["workspace"]["root"])
lanterna = root / ".vis" / "lanterna"
visroot = root
session_info, hits = await gather(
    read_session(),
    grep({"query": ["DefaultKeyDecodingProfile", "CarriageReturn", "KeyType.Enter", "case '\\r'", "case '\\n'", "\\u000d", "\\u000a", "getText()", "KeyType/Enter", "KeyType.Enter"], "paths": [str(lanterna / "src"), str(lanterna / "src/test"), str(visroot / "extensions/channels/vis-channel-tui")], "context": 4})
# Keep the required session read private; print only routing/current-turn shape and relevant code hits.
turns = session_info.get("transcript", {}).get("turns", []) if isinstance(session_info, dict) else []
print(f"session_read=yes turns={len(turns)}\n{hits}")