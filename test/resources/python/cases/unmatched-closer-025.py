shhist = await shell("git show --stat --oneline 3f1976a5 && git show --format=fuller --no-ext-diff 3f1976a5 -- VERSION pom.xml | head -100 && git show v3.1.5-vis.44:VERSION && git show v3.1.5-vis.44:pom.xml | grep -m1 '<version>'", cwd=str(lanterna))
await shhist.wait(20)
print(shhist.logs(-130)["out"])}