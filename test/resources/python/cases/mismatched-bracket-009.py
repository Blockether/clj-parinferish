print(patch('apps/vis-tui/test/com/blockether/vis/tui/projects_test.clj',[{'from':'181:5b6','to':'213:7d1','replace':'''(deftest project-request-order-and-race-test
  (let [workers (atom [])
        requests (atom [])]
    (with-redefs [state/app-db (atom (fixture-db))
                  vis/worker-future (fn [_ f] (swap! workers conj f))
                  vis/gateway-list-session-groups-page
                  (fn [opts] (swap! requests conj [:groups opts])
                    {:groups [] :total 0})
                  vis/gateway-list-sessions-page
                  (fn [opts] (swap! requests conj [:sessions opts])
                    {:sessions [{"id" "saved-outside-tui" "title" "Saved"}]
                     :total 40 :has-more true :next-cursor "next"})]
      (#'screen/request-project! project-a nil)
      (is (empty? @requests) "No gateway I/O or local view creation on input")
      ((first @workers))
      (is (= [:groups :sessions] (mapv first @requests)))
      (is (= :aside (get-in @requests [1 1 :grouped])))
      (is (<= (get-in @requests [1 1 :limit]) 30))
      (is (= "saved-outside-tui"
             (get-in @state/app-db [:project-sidebar :pages "a" :sessions 0 "id"])))
      (is (= 3 (count (:tabs @state/app-db))) "Pages must not allocate open views"))))
'''},{'from':'223:874','to':'225:aaa','replace':'''                 vis/gateway-list-session-groups-page
                 (fn [_]
                   (throw (ex-info "offline" {})))'''},{'from':'235:e37','to':'236:5cb','replace':'''     (is (= "a" (:active-project-id @state/app-db)))
     (is (str/includes? (get-in @state/app-db [:project-sidebar :pages "c" :error]) "Load failed"))'''},{'from':'259:e3d','replace':'                 (fn [_])\n                 (fn [_])))]'},{'from':'541:620','replace':'                (fn [_])\n                (fn [_])))'},{'from':'740:3b8','replace':'               (#\'screen/project-sidebar-key! (cap/key-stroke :down) select! add! refresh! menu! nil)))'},{'from':'741:028','replace':'         (#\'screen/project-sidebar-key! (cap/key-stroke :enter) select! add! refresh! menu! nil)'},{'from':'744:859','replace':'         (#\'screen/project-sidebar-key! (cap/key-stroke \\+) select! add! refresh! menu! nil)'},{'from':'747:95d','replace':'         (#\'screen/project-sidebar-key! (cap/key-stroke \\/) select! add! refresh! menu! nil)'},{'from':'748:028','replace':'         (#\'screen/project-sidebar-key! (cap/key-stroke :enter) select! add! refresh! menu! nil)'},{'from':'751:545','replace':'         (#\'screen/project-sidebar-key! (cap/key-stroke :esc) select! add! refresh! menu! nil)'},{'from':'753:377','replace':'         (is (nil? (#\'screen/project-sidebar-key! (cap/key-stroke \\a) select! add! refresh! menu! nil)))'},{'from':'1007:57d','replace':'                            (throw (ex-info "Wrong menu action" {})))\n                          (fn [_] nil))]'},{'from':'1200:57d','replace':'                            (throw (ex-info "Wrong menu action" {})))\n                          (fn [_] nil))]'},{'from':'1263:b33','replace':'                           (constantly nil)\n                           (constantly nil))'] }]))