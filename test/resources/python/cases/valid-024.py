srcpil = Path(pil).read_text()
tree = _ast.parse(srcpil)
classes = {}
for node in _ast.walk(tree):
    if isinstance(node, _ast.ClassDef):
        fns = [s.name for s in node.body if isinstance(s, _ast.FunctionDef)]
        attrs = [tg.id for s in node.body if isinstance(s, _ast.Assign) for tg in s.targets if isinstance(tg, _ast.Name)]
        classes.setdefault(node.name, (node.lineno, fns, attrs))
print(classes.get("_Draw"))
print(classes.get("_Kernel"))
print(classes.get("Color3DLUT"))
print(classes.get("MultibandFilter"))