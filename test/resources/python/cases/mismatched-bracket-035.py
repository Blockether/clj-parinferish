root=Path(session['workspace']['root'])
patches={
'test/com/blockether/vis/internal/progress_test.clj':[
 {'from':'7:c9d','replace':'  (it "stores form evaluation errors separately from printed output"'},
 {'from':'35:99e','to':'37:a29','replace':'      ;; Explicitly silent title changes stay in the timeline without a visible form\n      ;; or recap line.'},
 {'from':'46:c95','replace':''},
 {'from':'59:f28','replace':'           :stdout "1"'},
 {'from':'82:baa','replace':'        (on {:phase :form-result :iteration 1 :position 0 :code "work()" :stdout "done"})'
],
'test/com/blockether/vis/internal/gateway/state_test.clj':[
 {'from':'505:23d','to':'506:81b','replace':'                                :stdout "42"})]'},
 {'from':'2791:c6b','replace':'                                   {:turn_id tid :iteration 1 :form_index 0 :stdout "done"})'}
],
'test/com/blockether/vis/internal/loop_test.clj':[
 {'from':'1634:343','to':'1638:d96','replace':'  (it "never persists a bare evaluator return as a form fact"\n      (let [[envelope] (eng/blocks->forms [{:id 0 :code "value = 42" :result 42}]\n                                          {:turn 1 :iter 1})]\n        (expect (not (contains? envelope :result)))\n        (expect (nil? (form/result-card envelope)))))'},
 {'from':'1639:d2d','replace':'  (it "stores printed output once as stdout"'},
 {'from':'1642:e65','replace':'              [{:id 0 :code "print(\'hello\')" :stdout "hello\\n"}]'},
 {'from':'1707:050','to':'1709:75c','replace':'             ;; REGRESSION: the wall-clock BACKSTOP answered with only a timeout\n             ;; error. The guest never reaches its own `{:stdout}` outcome, so every line the\n             ;; block had already printed — the progress log of a long fetch loop, results already computed — died with'},
 {'from':'2007:fae','to':'2008:666','replace':'                        [{:scope "t1/i1/f1" :src "cat(\"a\")" :stdout "a"}\n                         {:scope "t1/i1/f2" :src "set_session_title(...)" :silent? true}]}'},
 {'from':'2013:021','replace':'                        :forms [{:scope "t2/i1/f1" :src "rg({...})" :stdout ""}]}]'},
 {'from':'2020:7cb','replace':'        (expect (= [{:scope "t1/i1/f1" :src "cat(\"a\")"}] (:results (first out)))) ; silent f2 excluded'},
 {'from':'2046:4d6','replace':'                             :filename "record.live.ndjson"'},
 {'from':'2058:feb','replace':'        (expect (str/includes? (first records) "record.live.ndjson"))'},
 {'from':'2074:e7e','replace':'                                            :silent? true}]}])'},
 {'from':'2089:32f','replace':'                                   :forms [{:scope "t1/i1/f1" :src "cat(x)" :stdout "x"}]}])'},
 {'from':'2109:c6b','to':'2111:632','replace':'                                   :forms [{:scope "t1/i1/f1" :src "cat(a)" :stdout "a"}\n                                           {:scope "t1/i2/f1" :src "cat(b)" :stdout "b"}\n                                           {:scope "t1/i2/f2" :src "cat(c)" :stdout "c"}]}])'}
],
'test/com/blockether/vis/internal/foundation/transcript_test.clj':[
 {'from':'14:cee','to':'25:08b','replace':''},
 {'from':'29:0e5','replace':'   clean turn with comment / stdout / a `(def ...)` var /'},
 {'from':'52:886','replace':'                          :forms [{:scope "t1/i1/f1" :tag :observation :src "(+ 1 1)" :stdout "2\\n"}]'},
 {'from':'223:353','to':'263:eab','replace':''},
 {'from':'319:f12','replace':'                                    [{:scope "t1/i1/f1" :tag :observation :src huge :stdout "ok\\n"}]'},
 {'from':'340:967','to':'342:643','replace':'                [{:scope "t1/i1/f1" :tag :mutation :src "(def x 1)"}\n                 {:scope "t1/i1/f2" :tag :mutation :src "(set-session-title! \\"Mixed\\")" :silent? true}\n                 {:scope "t1/i1/f3" :tag :observation :src "(read-file \\"a\\")" :stdout "a\\n"}]'},
 {'from':'366:b39','replace':'                                     [{:scope "t1/i1/f1" :tag :mutation :src code}]'},
 {'from':'428:75c','to':'431:00a','replace':'  "Regression for #40: a `python_execution` block\'s printed output rides\n   `:stdout` on the envelope. The forensic projection must surface it (data +\n   Markdown) without inventing a second success channel."'},
 {'from':'438:394','replace':'    (it "projects :stdout onto the block"'},
 {'from':'442:5c0','to':'445:294','replace':'    (it "does not fabricate stdout when Python printed nothing"\n        (let [b (->block 1 {:src "value = 1 + 1"})]\n          (expect (not (contains? b :stdout)))))'},
 {'from':'454:e31','to':'456:c21','replace':'    (it "omits the stdout section when there was no printed output"\n        (let [md (->md 0 false {:code "value = 1 + 1"})]\n          (expect (not (str/includes? md "_stdout:_")))))))'}
],
'test/com/blockether/vis/internal/foundation/introspection_test.clj':[
 {'from':'359:f0f','to':'370:b5e','replace':'                    ;; Nippy `:forms` (keyword-keyed) alongside `<-json` LLM maps\n                    ;; (string-keyed) — the mixed shape the verb must fully stringify.\n                    :forms [{:scope "t1/i1/f1"\n                             :tag :observation\n                             :src "print(\'echo hi\')"\n                             :op :print\n                             :stdout "echo hi\\n"}]'},
 {'from':'474:cfe','replace':'                                           :forms [{:src "print(2)" :stdout "2\\n"}]'},
 {'from':'498:cfe','replace':'                                      :forms [{:src "print(2)" :stdout "2\\n"}]'},
 {'from':'522:3af','to':'523:95f','replace':'                                             :forms [{:src (str "print(" (inc position) ")")\n                                                      :stdout (str (inc position) "\\n")}]'}
],
'test/com/blockether/vis/internal/compaction_verbs_test.clj':[
 {'from':'1226:8ba','replace':'                            :stdout "a"'},
 {'from':'1228:87f','replace':'             [2 {:forms-vec [{:scope "t1/i2/f1" :svar/tool-call-id "toolu_B" :stdout "b"}]}]]'}
]
}
for rel,edits in patches.items():
 print('===',rel,'===')
 print(await patch(root/rel,edits))