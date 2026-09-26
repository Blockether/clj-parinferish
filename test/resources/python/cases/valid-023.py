
srcpil = Path(pil).read_text()
tree = _ast.parse(srcpil)
classes = {}
modattrs = collections.defaultdict(list)
for node in _ast.walk(tree):
    if isinstance(node, _ast.ClassDef):
        fns = [s.name for s in node.body if isinstance(s, (_ast.FunctionDef, _ast.AsyncFunctionDef))]
        attrs = [tg.id for s in node.body if isinstance(s, _ast.Assign) for tg in s.targets if isinstance(tg, _ast.Name)]
        classes.setdefault(node.name, {"fns": fns, "attrs": attrs, "line": node.lineno})
    if isinstance(node, _ast.Assign):
        for tg in node.targets:
            if isinstance(tg, _ast.Attribute) and isinstance(tg.value, _ast.Name):
                if tg.value.id in ("ImageDraw", "ImageFilter"):
                    modattrs[tg.value.id].append(tg.attr)
for nm in ("_Draw", "_Kernel", "_BuiltinFilter", "Color3DLUT", "MultibandFilter"):
    print(nm, classes.get(nm))
print("ImageDraw attrs:", modattrs["ImageDraw"])
print("ImageFilter attrs:", sorted(set(modattrs["ImageFilter"])))
