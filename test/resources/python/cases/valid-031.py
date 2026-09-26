from pathlib import Path
root = Path(session["workspace"]["root"])

# Search the visible tree for existing commit-message guidance
import re
def grep(needle, paths, flags=""):
    out = []
    for p in paths:
        try:
            for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                if re.search(needle, line, re.I):
                    out.append(f"{p.relative_to(root)}:{i}: {line.strip()[:160]}")
        except Exception:
            pass
    return out

top_files = [p for p in root.iterdir() if p.is_file() and p.suffix in {".md", ".clj", ".edn", ".yml", ".yaml"}]
for needle in [r"commit", r"vis_session"]:
    for line in grep(needle, top_files):
        print(line)
    print("—")
