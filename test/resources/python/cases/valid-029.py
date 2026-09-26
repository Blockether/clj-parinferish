tree = _ast.parse(Path(pil).read_text())
cls_nodes = [n for n in _ast.walk(tree) if isinstance(n, _ast.ClassDef)]
print(len(cls_nodes))
names = [n.name for n in cls_nodes]
print(names[:10])
