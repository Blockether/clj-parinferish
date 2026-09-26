root = Path(session["workspace"]["root"])
rs, hits = await gather(
    read_session(),
    grep({"query": ["retire-python-worker", "interrupt-block!", "shared-key", "run-test-file!", "native-sleep", "retired"],
          "paths": [str(root / "src/com/blockether/vis/internal/python_worker.clj"),
                    str(root / "src/com/blockether/vis/internal/loop.clj"),
                    str(root / "src/com/blockether/vis/internal/language/python/python_test_runner.clj"),
                    str(root / "test/com/blockether/vis/internal/python_worker_test.clj"),
                    str(root / "test/com/blockether/vis/internal/language/python/test_fn_test.clj")],
          "context": 5})
summary = {"session_id": rs.get("id") if isinstance(rs, dict) else getattr(rs, "id", None),
           "turns": len(rs.get("transcript", {}).get("turns", [])) if isinstance(rs, dict) else None}
print("SESSION", summary)
print(hits)