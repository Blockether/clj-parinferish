print(edit_lines(R+"src/com/blockether/vis/internal/python_extensions.clj", 805, 822, [], "", "))
sh = await shell("cd /home/user/vis && git status --porcelain")
print((await sh.wait(30)).get("logs") or sh.logs())
