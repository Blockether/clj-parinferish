root = Path(session["workspace"]["root"])
rs, hits = await gather(
    read_session(),
    grep({"query": ["scrollIntoView", "scrollTo", "keyboard", "dismiss", "sendMessage", "handleSend", "composer", "message input"], "paths": [str(root / "apps/vis-companion/src")]})
print("SESSION", {"id": rs.get("id"), "turns": len(rs.get("transcript", {}).get("turns", []))} if isinstance(rs, dict) else type(rs).__name__)
print(hits)