r=patch(project_root_path/'test/com/blockether/vis/container_image_test.clj',[{'from':'90:ebc','replace':'                 text)))
  (it "prepares Java-bearing Git dependencies before AOT in a fresh container"
      ;; Regression: AOT failed to resolve vis-python-runtime.HostFunction in the
      ;; container because its Git dependency had never run :deps/prep-lib.
      (let [text (dockerfile)
            copied (str/index-of text "COPY . .")
            prepared (str/index-of text "RUN clojure -X:deps prep")
            compiled (str/index-of text "clojure -T:build native")]
        (expect (and copied prepared compiled (< copied prepared compiled))
                "The copied checkout must prep Git libraries before native AOT")))'}]); print(r); l=await clj.lint_code(paths=[str(project_root_path/'test/com/blockether/vis/container_image_test.clj')],cwd=str(project_root_path)); print('lint',l.errors,l.warnings,l.diagnostics[:3]); t=await clj.run_tests(paths=[str(project_root_path/'test/com/blockether/vis/container_image_test.clj')],cwd=str(project_root_path),timeout_s=120); print('regression before fix',t.total,t.passed,t.failed,[(x.test,x.message[:200]) for x in t.failures])