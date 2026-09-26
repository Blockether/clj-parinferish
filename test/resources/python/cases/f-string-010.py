H=f"-H 'Authorization: Bearer {tok}' -H 'X-Vis-Protocol: 2'"
r = await shell(cmd=f"curl -s -m 8 {H} http://127.0.0.1:7890/v1/capabilities | python3 -c 'import sys,json;d=json.load(sys.stdin);print(json.dumps(d.get(\"capabilities\",d).get(\"features\",{}).get(\"voice\"),indent=1))'")
print(r["stdout"], r["stderr"][:300])
v = await shell(cmd="cd ~/vis/apps/vis-companion && sleep 3; tail -5 /dev/null; true")
l = await shell(op="logs", id="vite", n=15)
print(l["lines"])