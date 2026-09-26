edits = [
    {"from": "29:9e4", "to": "29:9e4", "replace": "from cryptosyf.power import power_study\nfrom cryptosyf.snooping import reality_check"},
    {"from": "461:d01", "to": "466:4a2", "replace": '''def signal_screen(reader, registration):
    """One signal-only study, using the same verified cache and funding policy."""
    config = active_experiment(registration, "public-signal")
    provenance = []
    bars = load_verified_bars(reader, config["archive_months"], provenance)
    return {**study(bars, config), "rows": len(bars), "provenance": provenance}


def power_screen(reader, registration):
    """Preregistered sample-size planning report on the verified development cache."""
    config = active_experiment(registration, "public-power")
    provenance = []
    bars = load_verified_bars(reader, config["archive_months"], provenance)
    return {**power_study(bars, config), "rows": len(bars), "provenance": provenance}'''},
    {"from": "655:477", "to": "655:477", "replace": '''            "public-daily",
            "public-holdout",
            "public-power",
        }'''},
    {"from": "678:995", "to": "678:995", "replace": '''                "public-holdout": holdout_screen,
                "public-power": power_screen,''},  # placeholder, fixed below
]
# do it via plain text replace to avoid anchor ambiguity
src = (root/"src/cryptosyf/public_pilot.py").read_text()
src = src.replace(
    "from cryptosyf.snooping import reality_check",
    "from cryptosyf.power import power_study\nfrom cryptosyf.snooping import reality_check",
)
anchor = '''def signal_screen(reader, registration):
    """One signal-only study, using the same verified cache and funding policy."""
    config = active_experiment(registration, "public-signal")
    provenance = []
    bars = load_verified_bars(reader, config["archive_months"], provenance)
    return {**study(bars, config), "rows": len(bars), "provenance": provenance}
'''
addition = '''

def power_screen(reader, registration):
    """Preregistered sample-size planning report on the verified development cache."""
    config = active_experiment(registration, "public-power")
    provenance = []
    bars = load_verified_bars(reader, config["archive_months"], provenance)
    return {**power_study(bars, config), "rows": len(bars), "provenance": provenance}
'''
assert anchor in src and "power_screen" not in src
src = src.replace(anchor, anchor + addition)
src = src.replace(
    '''            "public-daily",
            "public-holdout",
        }''',
    '''            "public-daily",
            "public-holdout",
            "public-power",
        }''',
)
src = src.replace(
    '''                "public-holdout": holdout_screen,
            }''',
    '''                "public-holdout": holdout_screen,
                "public-power": power_screen,
            }''',
)
(root/"src/cryptosyf/public_pilot.py").write_text(src)
# CLI
m = (root/"src/cryptosyf/__main__.py").read_text()
m = m.replace(
    '''            "public-daily",
            "public-holdout",
        ],''',
    '''            "public-daily",
            "public-holdout",
            "public-power",
        ],''',
)
(root/"src/cryptosyf/__main__.py").write_text(m)
import subprocess as _sp  # not allowed; skip
ok = [s for s in ["power_screen", "public-power"] if s in src]
print("public_pilot wired:", ok, "| main wired:", "public-power" in m)