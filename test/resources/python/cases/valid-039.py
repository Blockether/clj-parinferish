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
print(len(old_strings), len(cur_strings))