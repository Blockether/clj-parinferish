prompt_path = root / "src/com/blockether/vis/internal/prompt.clj"
test_path = root / "test/com/blockether/vis/internal/prompt_test.clj"
prompt_edit = patch(prompt_path, [{
    "from": "365:8da",
    "to": "368:a8d",
    "replace": """    \"- At a research-to-implementation boundary, pressure is material when `last_request_tokens` is roughly 25% of\\n\"
    \"  `auto_compress_above` OR the sweep filled at least two clipped/max-sized tool results.\\n\"
    \"  If pressure is material and at least two requests remain, next iteration calls only\\n\"
    \"  `fold_session(\\\"-tN/iK\\\", gist)` before editing; `tN/iK` is the last completed research step,\\n\"
    \"  so the oldest settled prefix folds and the live step stays out.\\n\"""}])
test_edit = patch(test_path, [{
    "from": "237:c9c",
    "to": "247:03c",
    "replace": """               ;; Regression, user report: the benchmark said folding worked only because the task
               ;; ordered it. A real Z.ai GLM-5.3 Flash A/B run then showed that folding a 4k
               ;; settled prefix doubled cost, while the autonomous pressure run skipped its fold
               ;; after six clipped research results. Trigger on measured OR visible pressure plus
               ;; future requests, use one canonical oldest-prefix rewrite, and preserve small-task hits.
               \"research-to-implementation boundary\" \"`last_request_tokens` is roughly 25%\"
               \"`auto_compress_above` OR\" \"at least two clipped/max-sized tool results\"
               \"pressure is material and at least two requests remain\" \"next iteration calls only\"
               \"`fold_session(\\\"-tN/iK\\\", gist)`\" \"before editing\" \"last completed research step\"
               \"oldest settled prefix folds\" \"live step stays out\" \"one cache discontinuity\"
               \"one broad fold\" \"skip small or near-final work\" \"continue append-only\"
               \"gist must stand alone\" \"exact paths/symbols\" \"decisions,\"
               \"verification, edit/test state and dirty files\" \"confirm reduction\"]"""}])
print(prompt_edit)
print(test_edit)