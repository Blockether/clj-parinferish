print(cat(project_root_path / 'src/com/blockether/vis/internal/language/python/repl_manager.clj', 1, 12))
print('replacement boundary lines:', '\n'.join(manager_text.splitlines()[:12]), '\n...\n', '\n'.join(manager_text.splitlines()[-14:])))
test_callers = grep({'query':['repl/start!', 'repl/stop!', 'repl/status', 'repl/eval!', ':session-id test-session-id "env"'], 'paths':[str(project_root_path / 'test/com/blockether/vis/internal/language/python/repl_test.clj')], 'context':2, 'limit':100})
print(test_callers)