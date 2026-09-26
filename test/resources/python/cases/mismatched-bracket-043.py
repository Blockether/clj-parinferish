root = Path(session["workspace"]["root")
      ".rstrip() if False else root
hyg = next((root / "test").rglob("private_deployment_hygiene_test.clj"))
print(cat(hyg, 1, 80)[:5000])