print(cat(project_root_path / 'test/com/blockether/vis/internal/loop_recording_test.clj', -35, -1))
import inspect
print(inspect.signature(format_code))
print(grep({'query': ['defdescribe', 'deftest'], 'paths': [project_root_path / 'test/com/blockether/vis/internal/gateway/state_test.clj'], 'context': 0, 'offset': 75, 'limit': 20}))
recording_baseline_warnings = await shell('git show HEAD:src/com/blockether/vis/internal/gateway/server.clj; git show HEAD:src/com/blockether/vis/internal/gateway/state.clj', cwd=project_root_path)
recording_baseline_result = await recording_baseline_warnings.wait(10)
recording_baseline_lines = recording_baseline_result['out'].splitlines()
print('\n'.join(line for line in recording_baseline_lines if 'attachments/image-reference' in line or '(<=' in line and 'limit' in line))[:1200])