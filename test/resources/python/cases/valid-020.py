
import ast
srcpil = Path(pil).read_text()
tree = ast.parse(srcpil)
# find nested class defs anywhere
classes = {}
modattrs = collections.defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        fns = [s.name for s in node.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))]
        attrs = [tg.id for s in node.body if isinstance(s, ast.Assign) for tg in s.targets if isinstance(tg, ast.Name)]
        classes.setdefault(node.name, {"fns": fns, "attrs": attrs, "line": node.lineno})
for nm in ("_Draw","_Kernel","_BuiltinFilter","Color3DLUT","MultibandFilter"):
    print(nm, classes.get(nm))
# module-level assignment ImageDraw.X = ...
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for tg in node.targets:
            if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id in ("ImageDraw","ImageFilter"):
                modattrs[tg.value.id].append(tg.attr)
print("ImageDraw attrs:", modattrs["ImageDraw"])
print("ImageFilter attrs:", modattrs["ImageFilter"])
