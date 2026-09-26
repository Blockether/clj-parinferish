# Python repair corpus

Each file in `cases/` is one block of Python that a language model sent to the Vis
Python sandbox, copied from real sessions. The name gives the kind of mistake, as in
`unterminated-string-012.py`. The `valid-NNN.py` files are blocks CPython accepts;
the repair must leave them unchanged.

The blocks were scrubbed before they were added: home directories became
`/home/user`, user names `user`, personal addresses `example.com` and session ids
fixed placeholder UUIDs. Blocks about infrastructure or credentials, blocks larger
than 8 KB and blocks containing NUL bytes were left out.

`expected/<case>.txt` is the report for a case:

```text
cpython: <where and why CPython 3.14 refused the case, or ok>
result: valid | repaired | not repaired
fix: <one line per fix>
problem: <one line per problem>
--- text after repair
<the repaired text, when the repair changed it>
```

`result` is `repaired` when CPython parses the repaired text. The tests in
`python_test.clj` repair every case again and compare the report byte for byte;
with CPython 3.12 or newer installed, they also parse the repaired text.

## Improving the repair

1. Change the engine in `java/com/blockether/parinferish/python/` and run
   `clojure -T:build compile-java`.
2. Run `clojure -M:python-corpus`. It rewrites every report and prints the score,
   the cases that changed, and the time per case. It needs CPython 3.12 or newer as
   `$PYTHON` or `python3`.
3. Review the diff of `expected/`, then commit it with the change.

## Adding a case

Copy the block into `cases/<kind>-<next number>.py` byte for byte, scrub it as
described above, run `clojure -M:python-corpus`, and review its new report.
