root = Path(session["workspace"]["root"])
tui = root / "extensions/channels/vis-channel-tui"
h = await grep({"query": ["tui-usage", "--session-id ID", "channels tui ["], "parse-args"], "paths": [str(tui / "src"), str(tui / "test")], "context": 5, "limit": 140})
print(h)