per = await ci_failures(  # eeaa84e33 run id
  (await (async def_ := None)) if False else 0) if False else None
sh = await shell({"command": "cd ~/vis && gh run list -w ci.yml -b main -L 2 --json databaseId,headSha -q '.[] | [.databaseId,.headSha[0:9]] | @tsv'", "timeout": 120})
lg = sh.wait(120); print((lg.get("stdout") or "")[-150:])
