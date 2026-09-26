root = Path(session["workspace"]["root"])
h = await grep({"query": [":channel/owns-tty? false", ":channel/owns-tty? true", ":ext/channels ["], "channel/cmd"], "paths": [str(root / "extensions/channels"), str(root / "src")], "context": 3, "limit": 160})
print(h)