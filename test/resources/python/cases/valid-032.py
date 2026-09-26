import io as _io, tokenize
def indent_source(src, pad):
    """Indent Python source by `pad` spaces, leaving physical lines that sit
    inside multi-line string literals untouched."""
    inside=set()
    for tok in tokenize.generate_tokens(_io.StringIO(src).readline):
        if tok.type==tokenize.STRING and tok.end[0]>tok.start[0]:
            inside.update(range(tok.start[0]+1, tok.end[0]+1))
    out=[]
    for i,l in enumerate(src.splitlines(), start=1):
        out.append(l if (i in inside or not l.strip()) else pad+l)
    return "\n".join(out)

body_src = cand.split('"""\n',2)[2] if cand.startswith('"""') else cand   # drop the module docstring
body_src = body_src.lstrip("\n")
indented = indent_source(body_src, " "*8)

wrapper = '''# vis sandbox tabulate shim.
#
# The agent sandbox ships no tabulate wheel, so this file vendors upstream
# python-tabulate 0.9.0 (MIT, Copyright (c) 2011-2020 Sergey Astanin and
# contributors) verbatim, minus its packaging metadata and CLI entry point.
# The library body runs inside `_tabulate_module_body` so its names land in a
# real `tabulate` module instead of polluting the sandbox globals.


def __vis_install_tabulate__():
    import sys, types, builtins as _bi

    def _tabulate_module_body():
%s

        return locals()

    mod = types.ModuleType("tabulate")
    mod.__doc__ = "Pretty-print tabular data."
    for _k, _v in _tabulate_module_body().items():
        setattr(mod, _k, _v)
    sys.modules["tabulate"] = mod
    try:
        _bi.tabulate = mod.tabulate
    except Exception:
        pass


__vis_install_tabulate__()
del __vis_install_tabulate__
''' % indented

# prove the transform is AST-identical to the vendored body
orig_body = ast.parse(body_src).body
wrapped = ast.parse(wrapper)
fn = wrapped.body[0].body[1]           # def _tabulate_module_body
inner = fn.body[:-1]                   # drop `return locals()`
print("AST identical:", [ast.dump(a) for a in orig_body] == [ast.dump(b) for b in inner], len(orig_body), len(inner))
open("/tmp/wrapped_tabulate.py","w").write(wrapper)
print(len(wrapper))
