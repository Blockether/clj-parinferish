r=patch(project_root_path/'apps/vis-tui/test/com/blockether/vis/tui/projects_test.clj',[{'from':'1722:bb1','to':'1732:604','replace':'      (let [entry (first (filter #(= set-name (:label %)) entries))
            hit (first (filter #(= kind (:kind %)) (.current projects/hit-map)))
            expected [:menu (assoc entry :initial-action choice)]]
        (is (some? hit))
        (when hit
          (let [{:keys [col row]} (:bounds hit)
                click (MouseAction. MouseActionType/CLICK_DOWN 1
                                    (TerminalPosition. (int col) (int row)))]
            (is (= expected (projects/key-action db click)))))
        (is (= expected
               (projects/key-action (assoc-in db [:project-sidebar :index] (:index entry))
                                    (cap/key-stroke \+))))))'}]); print(r)