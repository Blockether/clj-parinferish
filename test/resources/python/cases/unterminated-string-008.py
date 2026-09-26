print(patch(t/'projects_test.clj',[{'from':'1845:bf7','to':'1848:34b','replace':'''         (is (= [:toggle-session "a" "s1"]
                (projects/key-action @state/app-db
                                     (MouseAction. MouseActionType/CLICK_DOWN 1
                                                   (TerminalPosition. (int (inc col)) (int row)))))))'''},{'from':'1906:f3b','replace':'  (let [initial (-> (grouped-db)
                    (assoc-in [:project-sidebar :expanded] #{"a"})
                    (assoc-in [:project-sidebar :pages "a"] {:sessions [] :grouped []}))'}]))