root = Path(session["workspace"]["root"])
turn_data, voice_hits = await gather(
    read_session(),
    grep({"query": ["voice", "Voice", "preview", "Preview", "playback", "audio"],
          "paths": [str(root / "apps" / "vis-companion" / "src")]})
print(voice_hits)
print({"session_id": turn_data.get("id") if isinstance(turn_data, dict) else None,
       "turns": len(turn_data.get("transcript", {}).get("turns", [])) if isinstance(turn_data, dict) else None})