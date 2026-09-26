print(grep({"query":["defn new-context", "workspace/root"], "paths":[project_root_path / "test/com/blockether/vis/test_python_context.clj"], "context":5}))
print(cat(project_root_path / "test/com/blockether/vis/internal/python/extensions_test.clj", 343, 426))
print(patch(project_root_path / "test/com/blockether/vis/internal/activity/event_test.clj", [{"from":"31:7ef", "replace":r'''(defdescribe compact-activity-paths-test
  (let [home (System/getProperty "user.home")
        project (str home "/activity-project")
        path (str project "/src/example.clj")
        sibling (str home "/activity-project-other/src/example.clj")
        ctx (event/context)
        invocation (event/invocation ctx nil)
        details {:operation :cat :presenter :generic :workspace-root project
                 :label path :args [path] :activity (presenter/for-tool :cat)
                 :started-at-ms (System/currentTimeMillis) :outcome :succeeded}]
    (it "compacts start, success and failure labels without changing argument identity"
      (let [start (event/start-event ctx invocation details)
            original (event/start-event ctx invocation (dissoc details :workspace-root))
            success (event/terminal-event ctx invocation
                                         (assoc details :result "1:abc│ /absolute/source/literal"))
            failure (event/terminal-event ctx invocation
                                         (assoc details :outcome :failed
                                                :error (ex-info (str "Cannot read " path) {})))]
        (expect (= "src/example.clj" (:label start)))
        (expect (= "src/example.clj" (get-in start [:presentation "summary"])))
        (expect (= (:argument-key original) (:argument-key start)))
        (expect (= "src/example.clj · lines 1–1" (get-in success [:presentation "summary"])))
        (expect (= "Cannot read src/example.clj" (:error-summary failure)))
        (expect (= [path] (:args details)))))
    (it "compacts authored sections, headings, text and table cells but preserves source and links"
      (let [literal (str "cat " path)
            url (str "https://gateway.example.com" path)
            view {"headline" "Listed directories" "summary" (str project " · " sibling)
                  "content" [{"type" "code" "text" literal}
                             {"type" "markdown" "text" (str "[source](" url ")")}
                             {"type" "text" "text" (str "File: `" path "` · " url)}]
                  "sections" [{"headline" path "summary" "1 file"
                               "content" [{"type" "heading" "text" sibling}
                                          {"type" "table" "columns" ["Path"]
                                           "rows" [[path] [sibling] ["/opt/external/example.clj"]]}]}]}
            public (:presentation (event/content-event ctx invocation details view))]
        (expect (= ". · ~/activity-project-other/src/example.clj" (get public "summary")))
        (expect (= "src/example.clj" (get-in public ["sections" 0 "headline"])))
        (expect (= "~/activity-project-other/src/example.clj"
                   (get-in public ["sections" 0 "content" 0 "text"])))
        (expect (= [["src/example.clj"] ["~/activity-project-other/src/example.clj"]
                    ["/opt/external/example.clj"]]
                   (get-in public ["sections" 0 "content" 1 "rows"])))
        (expect (= literal (get-in public ["content" 0 "text"])))
        (expect (= (get-in view ["content" 1]) (get-in public ["content" 1])))
        (expect (= (str "File: `src/example.clj` · " url)
                   (get-in public ["content" 2 "text"])))
        (expect (= path (get-in view ["sections" 0 "headline"])))))
    (it "compacts every built-in and custom renderer at the common event boundary"
      (doseq [operation [:ls :cat :grep :patch :format_code :lint_code :run_tests :custom.method]]
        (let [result {"path" path}
              terminal (event/terminal-event
                         ctx invocation
                         (assoc details :operation operation :result result
                                :activity {:headline "Check files"
                                           :render (fn [_ value]
                                                     {"headline" "Checked files"
                                                      "summary" (get value "path")
                                                      "content" []})}))]
          (expect (= "src/example.clj" (get-in terminal [:presentation "summary"])))
          (expect (not (:result-truncated terminal)))
          (expect (= path (get result "path"))))))))

(defdescribe unregistered-result-presentation-test'''.replace('\\','\\').replace('\n','
').replace('\"','"')}]))