root = Path(session["workspace"]["root"])
patch_path = Path.home() / ".vis" / "tmp" / "artifact-story-fixture.patch"
patch_path.parent.mkdir(parents=True, exist_ok=True)
selected_patch = header + hunks[1]
patch_path.write_text(selected_patch, encoding="utf-8")nsh = await shell(f"git apply --cached --check {shlex.quote(str(patch_path))}", cwd=root)
result = await sh.wait(30)
print(result.logs[-4000:] or "cached patch check passed")