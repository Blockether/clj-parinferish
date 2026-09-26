collision_sdk_test = '''@pytest.mark.parametrize("filename", ["issue176_demo.py", "issue176_bridge.py"])
def test_entrypoint_import_collision_has_actionable_error(tmp_path, monkeypatch, filename):
    # Issue #176: an entrypoint can shadow the package imported by its tool.
    import sys

    package = tmp_path / "src" / "issue176_demo"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "core.py").write_text("VALUE = 'OK'\\n", encoding="utf-8")
    entry = tmp_path / ".vis" / "extensions" / filename
    entry.parent.mkdir(parents=True)
    entry.write_text(
        "import importlib\\nimport blockether.vis.extension as vis\\n"
        "def ping():\\n"
        "    '''Return the implementation value.'''\\n"
        "    return importlib.import_module('issue176_demo.core').VALUE\\n"
        "vis.register(vis.Extension(name='issue176-collision', "
        "description='Import collision fixture', alias='issue176_demo', "
        "symbols=[vis.Symbol(ping)]))\\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(package.parent))
    monkeypatch.syspath_prepend(str(entry.parent))
    module_names = ("issue176_demo", "issue176_demo.core")
    for name in module_names:
        monkeypatch.delitem(sys.modules, name, raising=False)
    try:
        runpy.run_path(str(entry))
        declaration = vis._registration["spec"]
        ping = declaration["symbols"][0]["fn"]
        import_path = list(sys.path)
        for _ in range(2):
            if filename == "issue176_demo.py":
                with pytest.raises(ValueError, match="once per file") as error:
                    ping()
                message = str(error.value)
                assert "extension 'issue176-collision' is already registered" in message
                assert "If this happened during an import" in message
                assert "may be shadowing a package or module with the same name" in message
                assert "Rename the entrypoint" in message
                assert "demo.py -> demo_bridge.py" in message
                assert "public alias can stay unchanged" in message
            else:
                assert ping() == "OK"
            assert vis._registration["spec"] is declaration
            assert declaration["alias"] == "issue176_demo"
            assert sys.path == import_path
    finally:
        for name in module_names:
            sys.modules.pop(name, None)


'''
print(patch(registration_tests_path,[
    {'from':'50:9ac','replace':'    with pytest.raises(ValueError, match="once per file") as error:'},
    {'from':'54:000','replace':'    assert "extension \'greeter\' is already registered" in str(error.value)\n    assert "Keep a single registration in the entrypoint" in str(error.value)\n    assert vis._registration["spec"] is declaration\n'},
    {'from':'87:e30','replace':collision_sdk_test+'def test_object_tools_keep_method_metadata_and_raise_normally():'}
]))
collision_loader_test = '''(defdescribe entrypoint-import-collision-test
  ;; Issue #176: preserve import precedence and explain the entrypoint rename.
  (it "reports a colliding entrypoint and keeps a renamed bridge working across reloads"
    (with-shared-packages
      (fn [packages]
        (write-ext! packages "issue176_demo/__init__.py" "")
        (write-ext! packages "issue176_demo/core.py" "VALUE = 'OK'\\n")
        (doseq [[entry collision?] [["issue176_demo.py" true] ["issue176_bridge.py" false]]]
          (let [source (str "import importlib\\nimport blockether.vis.extension as vis\\n"
                            "def ping():\\n"
                            "    'Return the implementation value.'\\n"
                            "    return importlib.import_module('issue176_demo.core').VALUE\\n"
                            "vis.register(vis.Extension(name='issue176-collision', "
                            "description='Import collision fixture', alias='issue176_demo', "
                            "symbols=[vis.Symbol(ping, tag='observation')]))\\n")]
            (with-fresh-loaded {entry source}
              (fn [result {:keys [ext-dir]}]
                (expect (= 1 (:loaded result)) (pr-str (pyx/load-failures)))
                (expect (= 0 (:failed result)))
                (dotimes [generation 3]
                  (dotimes [_ 2]
                    (let [out ((symbol-fn (registered "issue176-collision") 'ping))]
                      (if collision?
                        (do
                          (expect (false? (:success? out)) (pr-str out))
                          (doseq [fragment ["extension 'issue176-collision' is already registered"
                                            "If this happened during an import"
                                            "may be shadowing a package or module with the same name"
                                            "Rename the entrypoint"
                                            "demo.py -> demo_bridge.py"
                                            "public alias can stay unchanged"]]
                            (expect (str/includes? (str (get-in out [:error :message])) fragment)
                              (pr-str out))))
                        (do
                          (expect (extension/envelope-success? out) (pr-str out))
                          (expect (= "OK" (:result out)) (pr-str out))))))
                  (when (< generation 2)
                    (write-ext! ext-dir entry (str source "# Reload " generation "\\n"))
                    (expect (= {:loaded 1 :failed 0 :changed? true}
                               (pyx/reload-python-extensions! {:dirs [(str ext-dir)]})))))))))))))
'''
print(patch(extension_tests_path,[{'from':'1680:ca8','to':'1710:efd','replace':collision_loader_test}]))
red_results = await gather(
    run_tests({'language':'clojure','ns':'com.blockether.vis.internal.python.extensions-test/entrypoint-import-collision-test'}),
    run_tests({'language':'python','cwd':str(project_root_path/'packages/vis-agent'),'paths':[str(registration_tests_path)],'runner':'project'})
)
for result in red_results:
    print(result)