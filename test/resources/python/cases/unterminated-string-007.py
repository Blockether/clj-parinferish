r=patch(str(t/'client_test.clj'),[{'from':'494:000','replace':'(deftest saved-session-page-query-omits-absent-filters-test
  ;; A nil cursor or filter must not become the literal string "nil" on the wire.
  (is (= "/v1/sessions?limit=10&project_id=a&grouped=aside"
         (#\'client/session-window-path {:limit 10 :project-id "a" :grouped :aside})))
  (is (= "/v1/sessions?ids=saved"
         (#\'client/session-window-path {:ids ["saved"]}))))

'}]); print(r)