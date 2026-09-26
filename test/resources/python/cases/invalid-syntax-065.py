> 
imports = set()
for p, t in big.items():
    for m in re.finditer(r"^\s*(?:import|from)\s+([A-Za-z_][\w.]*)", t, re.M):
        imports.add(m.group(1).split(".")[0])
print("third-party imports across the export layer:", sorted(imports - set(sys.builtin_module_names) - {"os","sys","argparse","math","pathlib","json","subprocess"}))
print("official config.py imports yaml:", "import yaml" in offtext["pocket_tts/utils/config.py"])
print("official utils.py imports requests:", "import requests" in offtext["pocket_tts/utils/utils.py"])