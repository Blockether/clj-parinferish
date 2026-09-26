SP="/home/user/spel/"
sh_i = await shell(f"""cd {SP} && gh issue create --repo Blockether/spel --title "A crashed renderer leaves the session lying: commands park for 25s, open() echoes the old URL, snapshot has no node budget" --body "$(cat <<'EOF'
Measured on the 0.9.26 native binary plus a rebuild of `main`, with deterministic scripts — no speculation. Three defects, one theme: **spel keeps answering as if the page were alive after the renderer is gone, and the snapshot walk has no budget at all.**

## R3 — a pending call parks for the full command budget after the renderer dies

```
spel --session s eval-js 'new Promise(()=>{})' &   # pending
kill -9 <chrome --type=renderer>
```

The pending `evaluate` does **not** get rejected by Playwright. It parks the whole 25 s command budget (measured 25042 ms) and only ends on spel's own interrupt. Every later command then answers `Target crashed` **forever**, and `health` still reports `ok — connected, page open`.

## R4 — with nothing in flight, `open` lies

Kill the renderer, then:

- `snapshot` / `eval-js` -> `Target crashed`, forever
- `open <url>` -> **rc=0 in 3 ms**, echoing the OLD url, without navigating
- `health` -> `ok`, `page open`

This is the mechanism behind \"the agent repeats itself\": the tool reports success for a navigation that never happened, so the caller retries the same step.

## R5 — the snapshot walk has no node budget

| DOM size | result |
| --- | --- |
| 15 000 elements | 641 ms, 537 KB |
| 150 000 elements | hit the 25 s budget, CANCELLED; renderer RSS 252 MB -> 628 MB |
| 600 000 elements | CANCELLED; renderer RSS 870 MB -> 1.95 GB |

The walk is what pushes the renderer into the memory pressure that kills it, and the caller gets nothing back for the 25 s.

## Playwright facts behind the fix (probed directly)

- `page.evaluate` on a spinning renderer parks; `Thread.interrupt` frees it in ~1 ms and the connection survives.
- `Locator.EvaluateOptions.setTimeout` does **not** bound JS execution — only element resolution.
- `Page.waitForFunction`'s timeout **is** driver-enforced (returned in 2003 ms against a spinning renderer).
- `page.onCrash` is the only signal that a renderer died; nothing else in the client rejects.

## Fix

Make the crash a first-class fact: record `onCrash` per page, end an in-flight command on the crash record instead of the 25 s clock, refuse to answer `open`/`snapshot`/`eval-js` from a crashed page (reopen a tab instead), surface it in `health`, and give the snapshot walk a node budget + deadline with an explicit `[partial snapshot: ...]` note and a `--max-nodes` escape hatch.
EOF
)" 2>&1 | tail -3""", id="ghissue")
print(sh_i.wait(90).get('stdout','')[-600:])
