context_script = companion / ".agents" / "skills" / "impeccable" / "scripts" / "context.mjs"
sh = await shell(f"node {shlex.quote(str(context_script))} --target src/components/ProviderAuth.tsx", cwd=str(companion))
ctx = await sh.wait(30)
source_region, test_region, ui_hits = await gather(
    cat(str(provider_file), 90, 230),
    cat(str(provider_test), 150, 310),
    grep({"query": ["Disclosure", "aria-expanded", "Chevron", "Accordion"], "paths": [str(companion / "src" / "components" / "ui.tsx"), str(companion / "src" / "components")]})
print("--- CONTEXT ---\n" + ctx)
print("\n--- SOURCE 90-230 ---\n" + source_region)
print("\n--- TEST 150-310 ---\n" + test_region)
print("\n--- UI HITS ---\n" + ui_hits)