root=Path(session["workspace"]["root"])
hits = grep({"query": ["gateway-client/request! :get", "session-id", '"session_id"', "/usage\"")], "paths": [root / "e2e", root / "test", root / "src"], "context": 4})
print(hits)