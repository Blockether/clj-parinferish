# clj-parinferish

Parinfer for Clojure source, in pure Java — a from-scratch rewrite of
[parinferish](https://github.com/oakes/parinferish) 0.8.0 by
[oakes](https://github.com/oakes), answering exactly what it answers, **hundreds of
times faster** — plus `balance`, the layer that decides when a repair may be written
to a file at all. Parinfer itself is [Shaun Williams](https://github.com/shaunlebron)'
design; see [Credits](#credits).

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

## Balancing an edit

Parinfer can always produce *a* repair. A tool that writes the result to a file needs
the other half: whether that repair is the caller's own omission put back, or a silent
semantic rewrite of code nobody in this call wrote. That decision is
`com.blockether.parinferish.balance`, and it is independent of who computes the repair —
it is HANDED a balancer, `String -> String | nil`.

```clojure
(require '[com.blockether.parinferish :as pf]
         '[com.blockether.parinferish.balance :as balance])

(balance/rebalance
 {:balancer      #(pf/repair % {:mode :indent})  ;; String -> String | nil
  :parses-clean? reads?                          ;; String -> boolean
  :source        spliced                         ;; the content the edit WOULD write
  :original      replaced                        ;; the text it replaced, when there is one
  :spans         [[12 15]]})                     ;; 1-based inclusive lines THIS call wrote
;; => {:ok? true :content "…" :notes ["line 14: added a closing )"]}
;; or {:ok? false :why "a repair exists, but it also closes line 31, which this edit did not write"}
;; or nil, when there is no balancer to ask
```

A candidate is written only when all four hold: it parses clean; it keeps the line count
and the final newline; every line it changes lies inside an edited span; and it only
**added** delimiters — one the caller typed is never deleted, moved or retyped, and every
other character, whitespace and line endings included, is theirs, in order. Fail one and
the edit is refused with its parse error intact, because a refusal is information and a
repair that reaches outside the edit is guessing about code this call never saw.

Indentation alone cannot say *where* a delimiter goes back, so the text the edit replaced
is the better witness and is tried first: a closer dropped from the middle of a line whose
code survived goes back in the middle, and a lost opener stops being indistinguishable from
one closer too many. The balancer's own answer is the fallback; after it come the closers
nothing else could place, appended at the end of the last line the call wrote, and a `"` the
replaced text proves ended that region — which no balancer can supply. The namespace
docstring argues every rule and the order they are tried in.

`changed-span` is public too: the 1-based inclusive line range in which two texts differ,
which is the `spans` most callers want.

### Checked, not asserted

`rebalance` is a decision, so it is pinned by its verdicts: 49 named cases over 88
assertions, each a candidate that must be accepted, or refused for a reason the caller can
act on. The extraction from vis was gated on more than that — 802 requests over 268 real
files and mutations of them, 255 repaired and 547 refused, verdict for verdict identical to
the code it came from — but that comparison ended with its other half. The suite is what a
reader can rerun.

## Compatibility

The claim is exactness, so it is checked rather than asserted. `dev/fuzz.clj` runs the
**real** parinferish 0.8.0 beside this implementation and compares the output byte for byte,
in all four modes, over whole files and over seeded mutations of them — a dropped closer, a
dropped opener, a dropped quote, an added closer, a deleted line, two swapped lines, a
re-indented line, a truncation, an inserted block. Point it at any tree:

```bash
clojure -M:fuzz ~/some/clojure/repo 2000   # directories to walk, then how many mutations
```

The run behind the claim: 446 files and 12.5 MB of Clojure — vis, spel, svar, clj-ruff and
this repo — plus 2,000 seeded mutations of them, in every mode. **9,784 comparisons, zero
disagreements.**

CI runs the same comparison on every push, over this repo and 400 mutations of it.

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
clojure -M:fuzz <dir>... [n]    # the same differential, over any tree
clojure -T:build jar            # target/parinferish.jar
```

The repo-root `PARINFERISH_VERSION` file is the single source of the version; the
release tag mirrors it. Pushing a `vX.Y.Z` tag deploys that version to Clojars and
cuts a GitHub release, and refuses to republish a version that is already there.

## Credits

The rules this library implements are not its own, and both authors gave them away
before anyone asked.

**Parinfer** is [Shaun Williams](https://github.com/shaunlebron)' idea and design:
indentation and delimiters carry the same information, so an editor can infer either
one from the other. His [interactive introduction](https://shaunlebron.github.io/parinfer/)
is still the best explanation of why that works, and the reference implementation,
[parinfer.js](https://github.com/parinfer/parinfer.js), is MIT — *Copyright (c) 2015
Shaun Williams and contributors*.

**[parinferish](https://github.com/oakes/parinferish)** is
[oakes](https://github.com/oakes)' Clojure library, and it — not parinfer proper — is
what this rewrite reproduces. It implements the three modes in its own way, and that
way, corner for corner, is the specification here: `dev/fuzz.clj` runs his 0.8.0
beside this implementation and compares the output byte for byte, so the behaviour
this README documents is his. He dedicated the project to the public domain under the
[Unlicense](http://unlicense.org/UNLICENSE), which asks for no acknowledgement at
all. It is owed regardless.

What is Blockether's here is the engine — an independent Java implementation of those
rules, linear where the original is quadratic — and `balance`, extracted from vis. No
upstream code was copied into either.

## License

MIT — see [LICENSE](LICENSE), which every jar carries as `META-INF/LICENSE` beside
[NOTICE](NOTICE), where the attribution above travels with the artifact.
