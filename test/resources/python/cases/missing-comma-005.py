print({name: type(globals().get(name)).__name__ for name in ("checks232", "format232", "red232")})
print(ls([project_root_path / "test/com/blockether/vis/internal", project_root_path / "scripts"], depth=1, pattern="*doc*"))
print(grep({"query": [":lint", ":format", "reflection", "clj-kondo", ":test"], "paths": [project_root_path / "deps.edn"], "context": 3}))
print(ap ropos("task") if False else "Lint/check batch interrupted by the running native host's missing FFM metadata; no verification verdict inferred.")