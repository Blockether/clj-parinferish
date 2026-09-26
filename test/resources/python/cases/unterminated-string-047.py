root = project_root_path
print(cat(root / "src/cryptosyf/journal.py"))
r = grep({"query": ["RESEARCH_COMMANDS = ", "^def ", "SWEEP", "SEPARATOR", "\"## \"], "paths": [str(root / "src/cryptosyf/comparison.py")], "context": 0})
print(r if isinstance(r, str) else r.get("stdout", r))