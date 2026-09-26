root = Path(session["workspace"]["root"])
app = root / "apps/vis-tui"
old = root / "extensions/channels/vis-channel-tui"
print(f"app={app.exists()} old={old.exists()} src={ (app/'src/com/blockether/vis/tui').exists()} test={ (app/'test/com/blockether/vis/tui').exists()}\nhandle={sh}
wait={res}")