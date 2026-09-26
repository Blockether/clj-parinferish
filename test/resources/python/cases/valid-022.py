
import ast
srcpil = Path(pil).read_text()
tree = ast.parse(srcpil)

def _cls_info(node):
    """Class name -> its methods, its class-level attribute names and its line."""
    fns = [s.name for s in node.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))]
    attrs = [tg.id for s in node.body if isinstance(s, ast.Assign) for tg in s.targets if isinstance(tg, ast.Name)]
    return {"fns": fns, "attrs": attrs, "line": node.lineno}

def _mod_attr(node, mods):
    """Names assigned onto one of `mods` (e.g. ImageFilter.BLUR -> ('ImageFilter','BLUR'))."""
    out = []
    for tg in getattr(node, "targets", []):
        ok = isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id in mods
        if ok:
            out.append((tg.value.id, tg.attr))
    return out

classes = {}
modattrs = collections.defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        classes.setdefault(node.name, _cls_info(node))
    if isinstance(node, ast.Assign):
        for mod, attr in _mod_attr(node, ("ImageDraw", "ImageFilter")):
            modattrs[mod].append(attr)

for nm in ("_Draw", "_Kernel", "_BuiltinFilter", "Color3DLUT", "MultibandFilter"):
    print(nm, classes.get(nm))
print("ImageDraw attrs:", modattrs["ImageDraw"])
print("ImageFilter attrs:", sorted(set(modattrs["ImageFilter"])))
