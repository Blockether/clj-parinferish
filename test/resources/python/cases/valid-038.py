old_src = old_plain['commands'][0]['stdout']
anchors_plain = cur_plain['results'][0]['anchors']
current_region = '\n'.join(v['text'] for k, v in sorted(anchors_plain.items(), key=lambda kv: int(kv[0].split(':')[0])))

def assignment_strings(src):
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            continue
        target = node.targets[0]
        if isinstance(target, ast.Attribute) and target.attr == '__doc__':
            out[target.value.id + '.__doc__'] = node.value.value
        elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == 'docs':
            out['docs.' + ast.literal_eval(target.slice)] = node.value.value
    return out

old_strings = assignment_strings(old_src)
cur_strings = assignment_strings('def _():\n' + current_region)
for name, old_value in old_strings.items():
    if name in cur_strings:
        a, b = len(old_value), len(cur_strings[name])
        print(f'{name}: {a} -> {b} ({(b / a - 1) * 100:.1f}%)')
for label, names in (
    ('callable docs', [k for k in old_strings if k.endswith('.__doc__')]),
    ('discovery docs', [k for k in old_strings if k.startswith('docs.')]),
):
    a = sum(len(old_strings[k]) for k in names)
    b = sum(len(cur_strings[k]) for k in names)
    print(f'{label}: {a} -> {b} ({(b / a - 1) * 100:.1f}%)')