app_baseline_full = await app_story_baseline_checked_sh.logs(-12000)
print('log keys:', list(app_baseline_full))
print('\n'.join(line for line in app_baseline_full['out'].splitlines() if 'BASELINE' in line))
print('\n'.join(line for line in app_baseline_node_checked.splitlines() if any(s in line for s in ['const repo', 'const names', 'originals =', 'if (source', 'BASELINE']))))