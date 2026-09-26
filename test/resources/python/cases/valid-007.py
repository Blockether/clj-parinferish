path = project_root_path / 'src/cryptosyf/comparison.py'
src = path.read_text()
# 1) fix Polish quote breaking the string
src = src.replace('"„B&H" to kupno', '„B&H” to kupno')
# 2) rewrite power measures to the real artifact shape
old_power = src[src.index("    power = artifacts.get(\"public-power\")"):src.index('    breadth = artifacts.get("public-breadth")')]
new_power = '''    power = artifacts.get("public-power")
    if power:
        mde = power.get("minimum_detectable_effect_at_observed_counts") or {}
        feasibility = power.get("feasibility") or {}
        effect = feasibility.get("effect_per_trade")
        measures = [
            "MDE na transakcję przy obserwowanej kadencji: "
            + ", ".join(
                f"{key.replace('_trades', ' trans.')}={_num(value, percent=True, signed=False)}"
                for key, value in sorted(mde.items())
            )
        ]
        for row in power.get("required_trades") or []:
            if row.get("effect_per_trade") != effect:
                continue
            years = row.get("years_at_trades_per_year") or {}
            cadence = sorted(int(key) for key in years)
            span = "/".join(
                f"{years[str(count)]:.1f}".replace(".", ",") for count in cadence[:3]
            )
            measures.append(
                f"horyzont {row.get('hold_hours')} h: {row.get('n_dependent')} niezależnych"
                f" transakcji; lat przy {('/'.join(str(c) for c in cadence[:3]))}/rok: {span}"
                f" (limit {feasibility.get('forward_years_max')} lat)"
            )
        measures.append(
            "kadencje obserwowane potwierdzają efekt "
            f"{_num(effect, percent=True, signed=False)} w limicie lat: "
            f"{'tak' if feasibility.get('any_observed_cadence_feasible') else 'nie'}"
        )
        feasible_cadence = sorted(
            {
                int(row.get("trades_per_year"))
                for row in feasibility.get("rows") or []
                if row.get("feasible_within_years")
            }
        )
        families.append(
            {
                "family": "Planowanie mocy (POWER-SOL-2025-v1)",
                "decision": power.get("status"),
                "measures": measures,
                "reasons": "raport planistyczny, nie decyzja",
                "unblock": (
                    "≥"
                    + "/".join(str(count) for count in feasible_cadence)
                    + " niezależnych transakcji/rok albo szerokość portfela"
                    if feasible_cadence
                    else "szerokość portfela poza jednym aktywem"
                ),
            }
        )
'''
src = src.replace(old_power, new_power)
path.write_text(src)
print("patched")

import sys, sqlite3, json
sys.path.insert(0, str(project_root_path / 'src'))
from cryptosyf import comparison
db = sqlite3.connect(str(project_root_path / 'data/public-pilot.sqlite'))
registration = json.loads((project_root_path / 'research/public-pilot.json').read_text())
artifacts = comparison.latest_complete_artifacts(db)
comp = comparison.build_comparison(artifacts, registration)
md = comparison.render_markdown(comp)
print("scenarios:", len(comp["scenarios"]), "families:", len(comp["families"]), "coverage:", len(comp["coverage"]), "md len:", len(md))
print(md[:2600])