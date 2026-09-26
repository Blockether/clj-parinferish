border_scope_out = border_scope_result['out']
border_initial_diff, border_initial_status = border_scope_out.split('\n M ', 1) if '\n M ' in border_scope_out else (border_scope_out, '')
print(border_initial_diff)
print(await border_baseline.wait(1))
print(cat(companion_path / 'src/components/LiveView.spacing.stories.tsx', 1, 210))
print(cat(companion_path / 'src/components/ChatContent.live.stories.tsx', 1, 56))
print(cat(companion_path / 'vitest.config.ts'))
print(cat(Path('/home/user/spel/AGENTS.md'))