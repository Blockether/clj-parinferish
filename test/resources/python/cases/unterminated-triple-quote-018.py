print(await patch(test_path,[{'from':'1121:353','to':'1155:de2','replace':'''  (it
    "replays the first inference after its warmup socket emits a terminal error"
    (let [events
          (atom [(completed-event "resp_warm" "")
                 (json/write-json-str {"type" "error"
                                       "error" {"code" "rate_limit_exceeded"
                                                "message" "Rate limit reached"}})
                 (completed-event "resp_1" "first")])

          sent
          (atom [])

          opens
          (atom 0)

          closes
          (atom 0)

          aborts
          (atom 0)

          factory
          (fake-websocket-factory events sent closes aborts)

          router
          (svar/make-router [{:id :openai-codex
                              :api-key "test-key"
                              :base-url "https://chatgpt.com/backend-api"
                              :api-style :openai-compatible-responses
                              :responses-path "/codex/responses"
                              :models [{:name "gpt-5.6" :context 100000 :input 1.0 :output 1.0}]}]
                            {:rate-limit {:same-provider-delays-ms [0 0]
                                          :respect-retry-after? false}})]

      (with-redefs [sut/open-responses-websocket! (fn [opts]
                                                    (swap! opens inc)
                                                    (factory opts))]
        (with-open [session (svar/open-session router
                                               {:routing {:provider :openai-codex
                                                          :model "gpt-5.6"}})]
          (expect (= "first" (:content (svar/ask! session "one"))))
          (let [[warmup first-attempt retry] @sent]
            (expect (false? (:generate warmup)))
            (expect (= "resp_warm" (:previous_response_id first-attempt)))
            (expect (nil? (:previous_response_id retry)))
            (expect (= [] (:input first-attempt)))
            (expect (= 1 (count (:input retry)))))))
      (expect (= 2 @opens))
      (expect (= 1 @aborts))))'}]))