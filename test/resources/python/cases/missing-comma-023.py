core_path = svar_root / "src/clj/com/blockether/svar/core.clj"
changelog_path = svar_root / "CHANGELOG.md"
results = await gather(
 patch(core_path, [{"from":"136:799","to":"137:f47","replace":"""  \"Wraps text in a cacheable content block. Anthropic emits `cache_control`.
   GPT-5.6+ Responses emits explicit prompt-cache breakpoints, including a
   rolling prior-turn boundary; older OpenAI-compatible styles strip the marker.\"""}]),
 patch(test_path, [{"from":"4:e09","to":"10:f89","replace":"""   These tests cover the wire-shape contract that downstream agent loops rely
   on for prompt caching:

   - `cached` markers survive `system`/`user`/`assistant` canonical content.
   - Anthropic emits `cache_control: {type: \"ephemeral\"}` per marked block.
   - GPT-5.6+ Responses emits exact rolling `prompt_cache_breakpoint` markers;
     older OpenAI wires strip unsupported `:svar/*` markers."""}]),
 patch(changelog_path, [{"from":"8:4ac","to":"9:000","replace":"""## [Unreleased]

### Fixed
- Reuse complete prior-turn prefixes on GPT-5.6 Responses with rolling explicit cache breakpoints.
"""}])
)
for x in results: print(x)