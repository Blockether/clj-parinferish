« print(patch(EPC, "3281:32d", "3282:b02", "\n".join([
    "      ;; `async def`, AUTO-SETTLES every bare tool-call STATEMENT at every depth (so",
    "      ;; `grep(x)` without `await` RUNS even inside `try:` or a `def`), drives it as",
    "      ;; a single coroutine, and reports"])))
print(patch(EPC, "3257:093", "3258:b8e", "\n".join([
    "   `__vis_run_async__` AST-wraps the block in an `async def`, AUTO-SETTLES every",
    "   bare tool-call STATEMENT at every depth (so `grep(x)` without `await` runs even",
    "   inside `try:` or a `def` body), drives it"])))

print(patch(EDC, "4478:7e3", "4483:fdb", "\n".join([
    "      (when (or (< n 1) (and (> n line-count) (not= which \"end\")))",
    "        (throw",
    "          (ex-info",
    "            (str \"cat: \" which \" line \" n \" is outside this file's 1..\" line-count \" lines.\")",
    "            {:type :ext.foundation.editing/invalid-range :which which :line n :lines line-count})))",
    "      ;; An END past EOF CLAMPS instead of refusing: `cat(path, 2172, 2212)` on a",
    "      ;; 2210-line file is a reader asking for the tail, and a refusal throws away",
    "      ;; everything the block printed before the call. A START past EOF still",
    "      ;; refuses — nothing is there to show and the address is genuinely wrong.",
    "      (min n line-count))))"])))
print(patch(EDC, "4441:798",
    "\n".join([
    "    anchor's line number) and only a genuinely unlocatable one refuses. A numeric",
    "    `end` past the last line CLAMPS to it — asking for the tail is not an error —",
    "    while a `start` past the end still refuses.\""])))

print(patch(PROMPT, "245:4a1", "246:cae", "\n".join([
    '    "  `struct_patch`, by ADDRESS with `patch(path, anchor, new)` for one line or\\n"',
    '    "  `patch(path, from_anchor, to_anchor, new)` for a span (`new=\\"\\"` deletes) — never\\n"',
    '    "  restate the text you replace: quote the anchor, not the file.\\n"'])))
