path = project_root_path / 'src/cryptosyf/comparison.py'
src = path.read_text()
src = src.replace('„B&H"', '„B&H”')
path.write_text(src)

import sys, sqlite3, json
sys.path.insert(0, str(project_root_path / 'src'))
from cryptosyf import comparison
db = sqlite3.connect(str(project_root_path / 'data/public-pilot.sqlite'))
registration = json.loads((project_root_path / 'research/public-pilot.json').read_text())
artifacts = comparison.latest_complete_artifacts(db)
comp = comparison.build_comparison(artifacts, registration)
md = comparison.render_markdown(comp)
md2 = comparison.render_markdown(comparison.build_comparison(comparison.latest_complete_artifacts(db), registration))
print("scenarios:", len(comp["scenarios"]), "families:", len(comp["families"]), "coverage:", len(comp["coverage"]))
print("deterministic:", md == md2, "| md len:", len(md))
print(md)