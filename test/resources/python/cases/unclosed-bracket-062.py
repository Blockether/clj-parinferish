from pathlib import Path
root = Path(session["workspace"]["root"]

msg = """chore(commits): minimal conventional commits that name their session

Subjects read as narrative essays and bodies restated the diff. From
2026-08-15T17:00Z every commit is type(scope): summary under 72 chars,
a body of at most six WHY lines, and a Vis-Session trailer;
test/com/blockether/vis/commit_convention_test.clj enforces it.

Vis-Session: vis_session_id#00000000-0000-4000-8000-000000000027"""

import tempfile, os
tmp = root/".git/COMMIT_MSG_VIS" if False else Path(tempfile.mkstemp(suffix=".txt")[1])
tmp.write_text(msg)

cmd = f"""cd {root} &&
git pull --rebase origin main &&
git add AGENTS.md CHANGELOG.md .agents/skills/release-vis/SKILL.md test/com/blockether/vis/commit_convention_test.clj &&
git commit -F {tmp} &&
git log -1 --stat --format='%h %s%n%b' &&
git push origin main"""
sh = await shell(cmd)
r = await sh.wait(30)
print(r["stdout"][-2500:] if r["stdout"] else r)
tmp.unlink(missing_ok=True)
