code = '''
def pil_classes(path):
    """Map every class in the PIL shim to (line, methods, class attrs)."""
    import ast
    tree = ast.parse(open(path).read())
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        fns = [s.name for s in node.body if isinstance(s, ast.FunctionDef)]
        attrs = []
        for s in node.body:
            if isinstance(s, ast.Assign):
                attrs += [t.id for t in s.targets if isinstance(t, ast.Name)]
        out.setdefault(node.name, (node.lineno, fns, attrs))
    return out

def pil_modattrs(path, mods):
    """Names assigned onto shim module objects, e.g. ImageFilter.BLUR."""
    import ast
    tree = ast.parse(open(path).read())
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id in mods:
                out.setdefault(t.value.id, []).append(t.attr)
    return out
'''
exec(compile(code, "<pilhelpers>", "exec"), globals())
C = pil_classes(pil)
M = pil_modattrs(pil, ("ImageDraw", "ImageFilter"))
for nm in ("_Draw", "_Kernel", "_BuiltinFilter", "Color3DLUT", "MultibandFilter"):
    print(nm, C.get(nm))
print("ImageDraw:", M.get("ImageDraw"))
print("ImageFilter:", sorted(set(M.get("ImageFilter", []))))
