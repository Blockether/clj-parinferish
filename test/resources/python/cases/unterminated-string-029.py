(IFACE/"pyproject.toml").write_text('''[project]
name = "vis-lang-interface"
version = "1.0.0"
description = "The shared contract for Vis language extensions, with exact JSON and TOML checks."
requires-python = ">=3.11"
dependencies = ["vis-agent>=0.2.10"]

[tool.vis]
category = "tools"
source_paths = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
# TestResult and TestFailure are contract types, not test cases: collect functions only.
python_classes = []
''', encoding="utf-8")

(IFACE/".gitignore").write_text(''".venv/
__pycache__/
.pytest_cache/
.ruff_cache/
*.log
''', encoding="utf-8")

(IFACE/"README.md").write_text('''# vis-lang-interface

The shared contract for [Vis](https://github.com/Blockether/vis) language extensions, written in
Python, plus the JSON and TOML tools it can serve on its own.

Vis knows nothing about programming languages. A language extension runs that language's own
toolchain and hands the model back a result; this package is what those results look like, so
`clj.lint_code` and `py.lint_code` read the same way and one presentation renders both.

## Install

```bash
vis-agent extension install Blockether/vis-lang-interface --global --trust
```

That gives you two tools under the `data` namespace:

```python
data.check(["config"])                      # parse every JSON and TOML file under config/
data.format(["package.json"], is_written=True)   # reformat JSON in place
```

`check` reports one located finding per file that does not parse. `format` rewrites JSON only
when you ask for it; TOML has no standard-library writer, so it is checked and never rewritten.

## Building a language extension on it

Add the package as a dependency of your extension and return its result types:

```toml
dependencies = [
  "vis-agent>=0.2.10",
  "vis-lang-interface @ git+https://github.com/Blockether/vis-lang-interface@v1.0.0",
]
```

```python
from vis_lang_interface import Diagnostic, LintResult, process, presentation

def lint(paths):
    done = process.run(["ruff", "check", "--output-format=json", *paths])
    return LintResult.of("python", _findings(done.out), files=len(paths))
```

| Module | What it gives you |
| --- | --- |
| `vis_lang_interface.results` | `Diagnostic`, `FormatResult`, `LintResult`, `TestResult`, `TestFailure`, `ReplResult`, `ReplSession` |
| `vis_lang_interface.process` | `run`, `tool_path`, `ToolRun`, `ToolMissing`, `ToolTimeout` |
| `vis_lang_interface.project` | `project_root`, `source_files` |
| `vis_lang_interface.presentation` | Activity rendering every language binding shares |
| `vis_lang_interface.data` | Exact JSON and TOML checks from the standard library |

## The extensions that use it

- [vis-lang-clojure](https://github.com/Blockether/vis-lang-clojure) — cljfmt, zprint, clj-kondo,
  Lazytest and an nREPL, through the `clojure` CLI.
- [vis-lang-python](https://github.com/Blockether/vis-lang-python) — ruff, pytest and a managed
  project REPL.

## Development

```bash
vis-agent python -m pytest tests -q
```
''', encoding="utf-8")

(IFACE/"AGENTS.md").write_text('''# vis-lang-interface

Python only. This repository is the contract every Vis language extension answers with; Vis
itself has no language contract and must never gain one.

- `src/vis_lang_interface/` is a library other extensions import as a Git dependency, and
  `extension.py` is the Vis entrypoint for the JSON and TOML tools it serves itself.
- Result types are frozen dataclasses with `Annotated` fields. Adding a field is a version bump
  for every extension that returns it; renaming one breaks them, so change names deliberately.
- Every exported method owns an explicit Activity presentation with a capitalized English label.
  Quick local reads use `show_start=False`. Cover success, failure and empty states in tests.
- Formatting and lint are ruff. Tests are pytest:
  `vis-agent python -m pytest tests -q` from the repository root.
- No Clojure, no JVM, no tree-sitter and no parser of our own: a verdict comes from the parser
  the language already ships.
''', encoding="utf-8")
print("ok")