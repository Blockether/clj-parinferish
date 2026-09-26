spel_skill, initial_hits = await gather(
    doc("spel"),
    grep({"query": ["JVM shutdown hook", "starting daemon", "start-daemon", "auto-connect", "ProcessBuilder", "daemon ready"],
          "paths": [str(spel_root / "src"), str(spel_root / "test")]})
print("--- SPEL SKILL ---\n" + str(spel_skill))
print("--- INITIAL CODE HITS ---\n" + str(initial_hits))