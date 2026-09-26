sdk_python = root / 'target/sdk-namespace/venv/bin/python'
provider_test_path = root / 'test/com/blockether/vis/internal/python/extensions_test.clj'
provider_repro_rows = anchored_source(provider_test_path)
provider_repro_index = next(i for i, (_, line) in enumerate(provider_repro_rows) if line == ';; Regression: a MANAGED provider declared by a PYTHON extension was a flag that')
provider_retry_test = '''(defdescribe python-provider-refresh-once-test
  (it "does not retry a refresh callback after its body raises"
    (with-loaded
      {"refresh_once.py"
       "import blockether.vis.extension as vis\ndef refresh(rejected=None):\n    vis.state['refresh_calls'] = vis.state.get('refresh_calls', 0) + 1\n    raise RuntimeError('fixture refresh failure')\ndef calls():\n    '''Read the number of refresh attempts.'''\n    return vis.state.get('refresh_calls', 0)\nvis.register(vis.Extension(name='refresh-once', description='Refresh regression', alias='once', symbols=[vis.Symbol(calls)], providers=[vis.Provider(id='refresh-once', label='Refresh once', refresh_token_fn=refresh)]))"}
      (fn [_ _]
        (let [provider (registry/provider-by-id :refresh-once)]
          (expect (nil? ((:provider/refresh-token-fn provider) "fixture-rejected")))
          (expect (= 1 (get-in ((symbol-fn (registered "refresh-once") 'calls)) [:result]))))))))

'''
# Escape the embedded Python newlines for the Clojure string, preserving its outer syntax.
start_py = provider_retry_test.index('"import blockether.vis.extension') + 1
end_py = provider_retry_test.index('"}', start_py)
provider_retry_test = provider_retry_test[:start_py] + provider_retry_test[start_py:end_py].replace('\n', '\\n') + provider_retry_test[end_py:]
print(await patch(provider_test_path, [{'from': provider_repro_rows[provider_repro_index][0], 'replace': provider_retry_test + provider_repro_rows[provider_repro_index][1]}]))
provider_baseline_sh = await shell(shlex.join([str(sdk_python), '-m', 'pytest', str(sdk_package/'tests/test_declarations.py'), str(sdk_package/'tests/test_registration.py'), '-q']), cwd=str(root))
provider_repl_start = repl_start(language='clojure', cwd=str(root))
print('test REPL:', {k: provider_repl_start.get(k) for k in ('status','error','id')})
print('missing test dependency:', sorted({f.get('message', '').splitlines()[-1] for f in provider_baseline.get('failures', [])})[:2])
read_regions([('packages/vis-agent/src/blockether/vis/extension.py', 1, 127), ('src/com/blockether/vis/internal/provider/limits.clj', 1, 180), ('resources/vis-docs/extending.md', 1004, 1173)])