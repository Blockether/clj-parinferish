tree = _ast.parse(Path(pil).read_text())
cls_nodes = [n for n in _ast.walk(tree) if isinstance(n, _ast.ClassDef)]
def cls_fns(n):
    return [s.name for s in n.body if isinstance(s, _ast.FunctionDef)]
def cls_attrs(n):
    return [t.id for s in n.body if isinstance(s, _ast.Assign) for t in s.targets if isinstance(t, _ast.Name)]
klass = {n.name: (n.lineno, cls_fns(n), cls_attrs(n)) for n in cls_nodes}
for nm in ("_Draw", "_Kernel", "_BuiltinFilter", "Color3DLUT", "MultibandFilter"):
    print(nm, klass.get(nm))
