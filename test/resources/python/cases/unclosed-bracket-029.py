clj_format, py_format = await gather(
  format_code({"language": "clojure", "paths": [str(root / "packages/vis-contract/resources/vis-contract/gateway.edn"), str(root / "packages/vis-contract/src/com/blockether/vis/contract/gateway.clj"), str(root / "test/com/blockether/vis/contract/gateway_test.clj")]}),
  format_code({"language": "python", "paths": [str(root / "packages/vis-contract/python/tests/test_contract.py")]})
print("CLJ\n" + str(clj_format) + "\nPY\n" + str(py_format))