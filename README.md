# clj-parinferish

Parinfer for Clojure source, in pure Java — a from-scratch rewrite of
[parinferish](https://github.com/oakes/parinferish) 0.8.0 that answers exactly
what upstream answers, **hundreds of times faster**.

```clojure
com.blockether/parinferish {:mvn/version "0.1.0"}
```

## Why

Upstream is one elegant Clojure file, and it re-matches eleven anchored regexes
against a **freshly copied remainder string** for every single token. That makes
repairing a file quadratic in its size: fine for the editor buffer it was written
for, ruinous for a tool that repairs whole namespaces.

Measured on this machine, indent mode, one repair of the whole file:

| source | lines | parinferish 0.8.0 | this | |
|---|---:|---:|---:|---:|
| synthetic namespace | 199 | 3.3 ms | 0.22 ms | 15× |
| synthetic namespace | 999 | 12.2 ms | 0.36 ms | 34× |
| synthetic namespace | 3 999 | 92.0 ms | 0.79 ms | 116× |
| synthetic namespace | 9 999 | 331.9 ms | 1.75 ms | 189× |
| synthetic namespace | 19 999 | 1 110.0 ms | 2.85 ms | **389×** |
| a real `editing/core.clj` | 6 240 | 1 049.8 ms | 2.85 ms | 368× |
| a real `internal/loop.clj` | 11 468 | 2 868.9 ms | 5.99 ms | **479×** |

Upstream's cost grows faster than the file; this one's does not. Reproduce with
`clojure -M:bench` (no arguments), or `clojure -M:bench path/to/file.clj`.

## Use

```clojure
(require '[com.blockether.parinferish :as pf])

(pf/repair "(defn f [x]\n  (inc x)" {:mode :indent})
;; => "(defn f [x]\n  (inc x))"

(let [result (pf/parse "(a b))\n" {:mode :indent})]
  [(pf/flatten result)   ;; => "(a b)\n"
   (pf/edits result)     ;; => [{:action :remove :offset 5 :line 0 :column 5 :text ")"}]
   (pf/error result)])   ;; => "Unmatched delimiter"
```

From Java, with no Clojure runtime at all:

```java
import com.blockether.parinferish.Parinfer;

String fixed = Parinfer.indentMode(source);
Parinfer.Result r = Parinfer.parse(source, Parinfer.Mode.PAREN);
```

### Modes

| mode | what it trusts | what it changes |
|---|---|---|
| `:indent` | the indentation | inserts, moves and drops closing delimiters |
| `:paren` | the delimiters | re-indents the lines |
| `:smart` | the cursor | indent mode before it, paren mode after it (`:cursor-line`, `:cursor-column`, zero-based) |
| `nil` | nothing | nothing — it only reads, and reports `error` |

A source whose **strings** do not terminate, or that ends a line on a backslash,
comes back verbatim in every mode. A file this library cannot read is a file it
must not rewrite.

## Compatibility

The claim is exactness, so the claim is checked rather than asserted.
`dev/fuzz.clj` runs the **real** parinferish 0.8.0 beside this implementation and
compares the output byte for byte, in all four modes, on whole files and on
seeded mutations of them — a dropped closer, a dropped opener, a dropped quote,
an added closer, a deleted line, two swapped lines, a re-indented line, a
truncation, an inserted block.

At the last full run: **617 real Clojure files** (16.9 MB of `.clj`/`.cljs`/
`.cljc`/`.edn`) and **3 961 mutations** of them, four modes each — **18 312
comparisons, zero disagreements**. A smaller version of the same suite is part
of the tests and runs in CI on every push.

### Divergences, on purpose

* **A form feed or a vertical tab** matched no upstream rule, so upstream stopped
  tokenizing and silently dropped the rest of the file. Here it is one more
  character the repair carries along.
* **`error`** reports the scanner's problem when there is one, because an
  unterminated string is *why* the reader then ran out of input. Upstream
  reported whichever error happened to be set last.
* **`edits`** is this library's own contract — action, offset, line, column and
  text, positioned in the original source — not a port of upstream's `diff`.
* The parse **tree** is not exposed. Only the repaired text, the edits and the
  error are.

## How it is fast

* One left-to-right scan fills parallel `int[]`/`byte[]` arrays: no regex, no
  `subs`, no per-token allocation.
* The repair appends *ops* (copy this source range, insert this character,
  insert these spaces) to one growable int buffer. A collection that turns out to
  end earlier than the reader thought simply truncates the buffer back to its
  last committed op — which is what upstream's index rewind did to its tree.
* Rendering is one `StringBuilder` pass over the ops. `edits` is computed only
  when it is asked for.
* No dependencies, no reflection, no resources, no shared state: every entry
  point is a pure function, safe on any thread, and needs no native-image
  configuration.

## Development

```bash
clojure -T:build compile-java   # java/ -> target/classes (needed once, and after any Java edit)
clojure -X:test                 # unit tests + the differential suite against upstream
clojure -M:bench                # the table above
clojure -T:build jar            # target/parinferish.jar
```

`resources/VERSION` is the single source of the version; the release tag mirrors
it. Pushing a `vX.Y.Z` tag deploys that version to Clojars and cuts a GitHub
release, and refuses to republish a version that is already there.

## License

MIT — see [LICENSE](LICENSE).

The behaviour reproduced here originates in
[parinferish](https://github.com/oakes/parinferish) by Zach Oakes, dedicated to
the public domain under the Unlicense. No code was copied: this is an
independent Java implementation of the same rules.
