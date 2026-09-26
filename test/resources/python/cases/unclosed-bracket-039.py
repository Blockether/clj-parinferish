runtime = root / "resources/vis-python/async_runtime.py"
test_path = root / "test/com/blockether/vis/internal/foundation/shell_test.clj"
transcript = view.get("transcript", {}) if isinstance(view, dict) else {}
current = view.get("current_turn", {}) if isinstance(view, dict) else {}
failures = view.get("failures", []) if isinstance(view, dict) else []
regions = await gather(
    cat(runtime, 900, 1075),
    cat(test_path, 320, 380),
    cat(test_path, 1180, 1235),
    grep({"query": ["__VisResult__", "__await__", "def __str__", "def __radd__", "cat("], "paths": [str(runtime), str(test_path), str(root / "test/com/blockether/vis/internal/python_runtime_test.clj")]})
print("CURRENT", str(current)[:4000])
print("FAILURES", str(failures)[-8000:])
print("RUNTIME\n" + str(regions[0]))
print("TEST EARLY\n" + str(regions[1]))
print("TEST LATE\n" + str(regions[2]))
print("OTHER HITS\n" + str(regions[3])[:12000])