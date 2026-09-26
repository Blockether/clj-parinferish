app=Path(session["workspace"]["root])/"apps/vis-companion/src"
print(grep({"query":[".queuedTurns(","queuedTurns("],"paths":[str(app)],"context":3})[:20000])
print(grep({"query":["status=queued"],"paths":[str(app/"lib/gateway.test.ts")],"context":8})[:12000])