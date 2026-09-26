sh=await shell("git status --short && printf '\n--- stat ---\n' && git diff --stat && printf '\n--- diff-check ---\n' && git diff --check",cwd=str(root))
print((await sh.wait(30))["out"]