print(await cat(str(root / "apps/vis-companion/src/components/LiveView.tsx"), 1, 120))
print(await cat(str(root / "apps/vis-companion/src/lib/live-view.ts"), 1, 100))
print(await grep({"query": ["human-input/live-close", "live.close", "live-close"], "paths": [str(root / "apps/vis-companion/src"), str(root / "test/com/blockether/vis/internal/gateway")]})