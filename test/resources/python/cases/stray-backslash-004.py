root=str(Path(session['workspace']['root']))
sh=await shell("rg -n 'root-command|Run a registered channel|:cmd/name \\"channels\\"' src/com/blockether/vis/internal/main.clj src/com/blockether/vis/internal/registry.clj",cwd=root)
await sh.wait(20)
print(sh.logs(-60))