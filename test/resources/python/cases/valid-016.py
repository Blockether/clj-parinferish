root = Path(session["workspace"]["root"])
p = root / ".vis/extensions/gh.py"
lines = p.read_text().splitlines()

def find(needle, start=0):
    for i in range(start, len(lines)):
        if needle in lines[i]:
            return i + 1  # 1-based
    return None

marks = {
    "imports": find("import calendar"),
    "ghmissing": find("class GhMissing"),
    "repo_flag": find("def _repo_flag"),
    "gh_login": find("def gh_login"),
    "require_gh": find("def require_gh"),
    "fetch_run": find("def fetch_run"),
    "newest_run": find("def newest_run"),
    "model_report": find("def _model_report"),
    "watch_close": find("selection_snapshots = ("),
    "gh_watch_run": find("def gh_watch_run"),
    "fetch_checks": find("def fetch_checks"),
    "prompt": find("PROMPT = "),
    "vis_ext": find("vis.extension("),
}
print(json.dumps(marks, indent=0))
print("TOTAL", len(lines))
# print the tight regions I will patch
for name in ("watch_close",):
    at = marks[name]
    print(f"--- {name} @{at} ---")
    print(cat(p, at - 2, at + 40))
