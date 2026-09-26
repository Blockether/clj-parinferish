import sys, traceback, json, hashlib
from pathlib import Path
sys.path.insert(0, str(project_root_path / 'src'))
from cryptosyf.public_pilot import comparison_screen, REGISTRY_PATH
from cryptosyf.public_data import PublicReader, PublicDataBlocked
import sqlite3

store = str(project_root_path / 'data/public-pilot.sqlite')
registry_bytes = REGISTRY_PATH.read_bytes()
registration = json.loads(registry_bytes)
try:
    with PublicReader(store, allow_network=False) as reader:
        result = comparison_screen(reader, registration)
        result["funding_policy"] = registration["current_funding_policy"]
        result["registry_sha256"] = hashlib.sha256(registry_bytes).hexdigest()
        result["code_sha256"] = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(public_pilot_file := str(project_root_path / 'src/cryptosyf/public_pilot.py')).parent if False else Path(sys.modules['cryptosyf.public_pilot'].__file__).parent.glob("*.py"))
        }
        result["usage"] = reader.audit()
        artifact = reader.save_result("public-comparison", result)
        print("saved artifact:", artifact)
except Exception:
    print(traceback.format_exc())