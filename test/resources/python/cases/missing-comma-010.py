snapshot_path = project_root_path / 'target/council-scoped-validation-eb8e3b56-t12'
snapshot_path.mkdir(exist_ok=False)
scoped_tree = 'da787bf741dbc82802df32c79faaa04b7889c95a'
snapshot_export = await shell('git checkout-index --all --prefix=' + shlex.quote(str(snapshot_path) + '/') + ' && git diff --cached --name-only && git write-tree', cwd=project_root_path)
print(await snapshot_export.wait(20))
print(ap ropos if False else 'Standalone index export; no clone or worktree created.')