sqlite_tree, view_event_hits = await gather(
    ls(str(sqlite_root / "src"), depth=8),
    grep({"query": [":view/open", ":view/patch", ":view/close", "view.open", "view.patch", "view.close", "iteration.completed"], "paths": [str(gateway_dir / "state.clj"), str(root / "src/com/blockether/vis/internal/view.clj")]})
regions = await gather(
    cat(str(root / "src/com/blockether/vis/internal/view.clj"), 2000, 2160),
    cat(str(gateway_dir / "state.clj"), 1248, 1348),
    cat(str(gateway_dir / "state.clj"), 1380, 1570),
    cat(str(gateway_dir / "state.clj"), 1900, 1990),
    cat(str(gateway_dir / "state.clj"), 2250, 2350),
    cat(str(schema), 340, 432),
    cat(str(schema), 650, 730)
)
print("SQLITE TREE\n", sqlite_tree)
print("\nVIEW EVENT HITS\n", view_event_hits)
for label, part in zip(["VIEW CLOSE", "DESCRIPTORS", "EVENT BUILD", "ITER COMPLETE", "TRACE", "ITER SCHEMA", "ATTACHMENT SCHEMA"], regions):
    print("\n====", label, "====\n", part)