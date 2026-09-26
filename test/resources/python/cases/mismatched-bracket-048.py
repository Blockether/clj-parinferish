from pathlib import Path
import tempfile
root = Path(session["workspace"]["root")

msg = """chore(commits): minimal conventional commits that name their session

Subjects read as narrative essays and bodies restated the diff. From
2026-08-15T17:00Z every commit is type(scope): summary under 72 chars,
a body of at most six WHY lines, and a Vis-Session trailer;
test/com/blockether/vis/commit_convention_test.clj enforces it.

Vis-Session: vis_session_id#00000000-0000-4000-8000-000000000027"""

tmp = Path(tempfile.mkstemp(suffix=".txt")[1])
tmp.write_text(msg)

sh = await shell(
    f"cd {root} && "
    "git add AGENTS.md CHANGELOG.md .agents/skills/release-vis/SKILL.md test/com/blockether/vis/commit_convention_test.clj && "
    f"git commit -F {tmp} && "
    "git push origin main && "
    "git log -2 --format='%h %cI %s'"
)
r = await sh.wait(40)
print(r["stdout"][-2000:] if r.get("stdout") else r)
tmp.unlink(missing_ok=True)
