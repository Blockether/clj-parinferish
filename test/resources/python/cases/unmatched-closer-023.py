print("INPUT CONTEXT BY ITERATION (provider measurements)")
for iteration in reported_iters:
    p = iteration["position"]
    if p <= 2 or 42 <= p <= 51 or p >= 64:
        print(json.dumps({k: iteration.get(k) for k in ["position", "input_tokens", "input_cache_read_tokens", "input_regular_tokens", "input_cache_write_tokens", "prompt_cache_continuity", "prompt_cache_reusable_tokens", "status", "created_at"]}))
fold_iter = next(i for i in reported_iters if i["position"] == 46)
print("FOLD STDOUT", [b.get("stdout", b.get("result")) for b in fold_iter["blocks"]])
print("HEALTH BREAKDOWN AROUND FOLD")
for iteration in reported_iters:
    if iteration["position"] in [44, 45, 46, 47, 48, 64, 68]:
        health = iteration.get("request_health", {})
        print(iteration["position"], {k: health.get(k) for k in ["breakdown", "budget_tokens", "reminder_tokens", "model_input_limit"]})
print("POST-FOLD RECOVERY/REPEAT SIGNALS")
for iteration in reported_iters:
    if iteration["position"] > 46:
        for block in iteration.get("blocks", []):
            code = block.get("code", "")
            matched = [name for name in ["read_session", "fold_session", "cat(", "grep(", "run_tests", "patch("] if name in code]
            if matched:
                print(iteration["position"], matched, "code_chars", len(code), "stdout_chars", len(str(block.get("stdout", "")))))