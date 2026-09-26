res = await patch(t, [{"from":"224:2b5","to":"224:2b5","replace":"""  ;; Regression, user report: selecting a nested source file with tests owned by
  ;; its nearest parent suite was answered with no test namespaces.
  (it \"resolves a nested SOURCE file to the nearest parent *-test namespace\"
      (with-project (assoc thing-test-file
                      \"src/com/example/thing/detail.clj\" \"(ns com.example.thing.detail)\\n\")
                    (fn [root]
                      (expect
                        (= [\"com.example.thing-test\"]
                           (:nses
                            (run-capturing
                              root
                              {\"paths\" [\"src/com/example/thing/detail.clj\"]})))))))
  (it \"walks a directory for every test namespace under it\"""}])
print(res)