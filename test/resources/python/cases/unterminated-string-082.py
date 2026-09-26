print(await patch(str(main_test), [{"from":"90:4e4", "replace":"            (expect (= [:clojure] @calls) (pr-str args))))}]))
res = await run_tests({"language":"clojure","paths":["test/com/blockether/vis/internal/main_test.clj::dispatch-extension-initialization-test"]})
print(res)