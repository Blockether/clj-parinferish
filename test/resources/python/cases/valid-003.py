import re
app = project_root_path / "apps" / "vis-companion"
p = app/"src"/"components"/"ui.test.tsx"
lines = p.read_text().splitlines()
# map describe blocks: top-level describe with line ranges
starts = [(m.start(), m.group(1)) for m in re.finditer(r'(?m)^describe\(', p.read_text())]
src = p.read_text()
bounds = [m.start() for m in re.finditer(r'(?m)^(describe|it)\(', src)]
blocks = []
for i, (pos, _) in enumerate(starts):
    end = starts[i+1][0] if i+1 < len(starts) else len(src)
    body = src[pos:end]
    line0 = src[:pos].count("\n")+1
    blocks.append((line0, src[:end].count("\n")+1, starts[i][1], body))
def cat(body):
    raws = len(re.findall(r'\b\w+Source\b', body))
    static = 'renderToStaticMarkup' in body
    paint = len(re.findall(r"'(bg|text|border|rounded|shadow|gap|p[xytrbl]?|m[xytrbl]?|w-|h-|flex|grid|items|justify|font|leading|tracking|opacity|min-w|min-h|max-w)[-\w/()\[\].%]*'", body))
    aria = len(re.findall(r"aria-|role=|getBy|announce|label", body))
    return raws, static, paint, aria
print(f"{'lines':>12}  {'rawrefs':>7} {'static':>6} {'paint':>5} {'aria':>4}  describe")
for line0, line1, name, body in blocks:
    raws, static, paint, aria = cat(body)
    first = body.split("(")[1].split("'")[1][:58] if "(" in body else name
    print(f"{line0:>5}-{line1:<6}  {raws:>7} {str(static):>6} {paint:>5} {aria:>4}  {first}")
tot_paint = sum(cat(b)[2] for b in [x[3] for x in blocks])
print("\ntotal paint-ish quoted class tokens:", tot_paint)