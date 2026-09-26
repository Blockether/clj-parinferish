print(patch(project_root_path/'test/com/blockether/vis/internal/activity/presenter_test.clj',[{'from':'299:339','to':'303:62e','replace':'  (it "shows a running shell command and output without repeating its status"
      (let [value {:command "npm run storybook" :exit nil :status "running"}
            command [{"type" "heading" "text" "Command"}
                     {"type" "code" "language" "bash" "text" "npm run storybook"}]
            running (presenter/result-presentation {:operation :shell} value)
            with-output (presenter/result-presentation {:operation :_shell-logs}
                                                       (assoc value :out "Server ready"))]
        (expect (= "Running command" (get running "headline")))
        (expect (= command (get running "content")))
        (expect (= (into command [{"type" "heading" "text" "Output"}
                                  {"type" "code" "text" "Server ready"}])
                   (get with-output "content")))))'}]))