tree = _ast.parse(Path(pil).read_text())
klass = {}
for node in _ast.walk(tree):
    if isinstance(node, _ast.ClassDef):
        fns = [s.name for s in node.body if isinstance(s, _ast.FunctionDef)]
        attrs = [t.id for s in node.body if isinstance(s, _ast.Assign) for t in s.targets if isinstance(t, _ast.Name)]
        klass.setdefault(node.name, (node.lineno, fns, attrs))
print(klass.get("_Draw"))
print(klass.get("_Kernel"))
print(klass.get("Color3DLUT"))
print(klass.get("MultibandFilter"))
