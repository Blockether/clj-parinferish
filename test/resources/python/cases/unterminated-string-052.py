sh = await shell("cd /home/user/CryptoSyf && PYTHONPATH=src vis-agent python -c \"
import traceback
from cryptosyf import fvg_study, public_pilot
try:
    result = fvg_study.run_study()
except Exception:
    traceback.print_exc()
\" 2>&1 | tail -40")
w = await sh.wait(300)
print("exit:", w["exit"])
print(sh.logs(-40))
