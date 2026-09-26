print(cat(tui_src / 'render.clj', 6060, 6395))
print(grep({'query': ['defn.*detail-(node-id|expanded)', 'toggle-details', 'defn.*activity'], 'paths': [tui_src / 'state.clj', tui_src / 'render.clj'], 'is_regex': True, 'context': 2, 'limit': 60}))
print(grep({'query': ['operation-group', 'argument-group', 'group.*(click|toggle|expand|disclosure)', 'disclosure.*(independent|group)'], 'paths': [tui_test / 'render_test.clj', tui_test / 'screen_test.clj', tui_test / 'state_test.clj'], 'is_regex': True, 'context': 2, 'limit': 55}))
history_snippets = []
for tr in activity_history['transcript']['turns']:
    for it in tr.get('iterations', []):
        for b in it.get('blocks', []):
            for key in ['stdout', 'code']:
                text = b.get(key)
                if isinstance(text, str):
                    for m in re.finditer(r'(?:[^
]*(?:detail-expansions|activity-operation-rows|activity-expanded\?|group.*toggle|toggle.*group)[^
]*)', text, re.I):
                        history_snippets.append((tr['position'], it['position'], key, m.group(0)[:400]))
print('Related saved evidence:', history_snippets[-15:])