sh = await shell("cd /home/user/CryptoSyf && PYTHONPATH=src vis-agent python uv run --no-sync python -c \"
from cryptosyf import public_pilot, sar_study
import tempfile, pathlib
from cryptosyf.public_data import PublicReader
print('job dispatch:', public_pilot.job('public-sar'))
with tempfile.TemporaryDirectory() as tmp:
    with PublicReader(pathlib.Path(tmp) / 'p.sqlite') as reader:
        result = public_pilot.sar_screen(reader, public_pilot.load_registration() if hasattr(public_pilot, 'load_registration') else __import__('json').loads(pathlib.Path('research/public-pilot.json').read_text()))
        print('cache-miss status:', result['status'], '| failure:', result['failure'], '| attempts:', reader.audit()['attempts'])
\"")
print(sh.wait(60))
