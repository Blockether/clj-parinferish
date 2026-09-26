r=patch(project_root_path / 'apps/vis-tui/test/com/blockether/vis/tui/dialogs_test.clj',[
 {'from':'2539:dd5','replace':'  (it "paints a single-cell favorite mark on the starred row alone"'},
 {'from':'2565:c0f','replace':'                (expect (str/includes? (line 0) "* Deploy"))'},
 {'from':'2567:cc9','replace':'                (expect (not (str/includes? (line 4) "* Deploy"))))'},
 {'from':'2569:000','replace':'(defdescribe
  model-picker-portable-marker-test
  (it "labels the reset choice with the same single-cell favorite mark"
      (with-redefs [vis/picker-fleet (constantly [])
                    dlg/list-dialog! (fn [_ title items opts]
                                       {:title title :items items :opts opts})]
        (let [{:keys [title items opts]} (dlg/model-picker! nil nil)]
          (expect (= "Session model" title))
          (expect (= "* router default" (:label (first items))))
          (expect (true? (:reset? (first items))))
          (expect (:filter? opts))))))
'}])
print(r)