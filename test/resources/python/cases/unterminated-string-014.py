r=await uplink.run("python3.12 - <<'PY'
import importlib.util
print({name:bool(importlib.util.find_spec(name)) for name in ['torch','onnxruntime','transformers','laya','numpy','huggingface_hub']})
PY"); print(r.exit_code,r.stdout,r.stderr[:300]); print('mac',typed_int8.logs(-2)['out'][-220:],typed_int8['status'])