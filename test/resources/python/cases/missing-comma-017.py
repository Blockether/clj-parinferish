commit_status_lines = await local_command('git status --porcelain=v1 --untracked-files=all')
assert commit_status_lines.get('exit') == 0, 'Cannot capture repository status'
commit_status_text = commit_status_lines.get('out', '').replace('\r\n', '\n')
commit_paths = [line[3:] for line in commit_status_text.splitlines() if line]
assert all(' -> ' not in path and not path.startswith('"') for path in commit_paths), 'Status needs rename/quoted-path parsing'
def captured_worktree(paths):
    """Capture exact worktree bytes and executable modes for a fixed Git scope."""
    captured = {}
    for name in paths:
        path = project_root_path / name
        if path.is_symlink():
            captured[name] = ('120000', os.readlink(path).encode())
        elif path.is_file():
            captured[name] = ('100755' if path.stat().st_mode & 0o111 else '100644', path.read_bytes())
        else:
            captured[name] = None
    return captured
commit_initial_files = captured_worktree(commit_paths)
commit_initial_head = '43e687f388ac6c64a00dad8bc7c7a8cd04349d18'
commit_initial_index = await local_command('git diff --cached --binary --no-ext-diff && git ls-files --stage -- ' + ' '.join(shlex.quote(path) for path in commit_paths))
print({'captured_paths': commit_paths, 'index_exit': commit_initial_index.get('exit'), 'snapshot_bytes': sum(len(value[1]) for value in commit_initial_files.values() if value)})
print(grep({'query': ['"scripts"', 'vitest', 'lint', 'pre-commit', 'pre-push'], 'paths': [str(project_root_path / 'apps/vis-companion/package.json'), str(project_root_path / 'deps.edn')], 'context': 3}))
print({'guidance': [str(path.relative_to(project_root_path)) for base in ['apps', 'apps/vis-companion', 'apps/vis-companion/src', 'apps/vis-companion/src/components'] for path in (project_root_path / base).iterdir() if path.name == 'AGENTS.md'], 'hook_roots': [path.name for path in project_root_path.iterdir() if 'hook' in path.name or path.name in {'.github', '.git'}]})
print(doc('design'))
print(aprop os('x') if False else apropos('^(run_tests|lint_code|format_code|repl_status|repl_stop)$'))