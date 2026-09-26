results=await gather(
 patch(app/'src/com/blockether/vis/tui/provider.clj',[
  {'from':'336:f8f','to':'350:857','replace':'(defn- save-provider-config!\n  "Ask the gateway to add one preset-backed provider; this client never writes its fleet."\n  [provider]\n  (vis/gateway-add-provider! (:id provider) (:base-url provider))\n  provider'},
  {'from':'1062:ece','to':'1062:ece','replace':'    (when config (save-provider-config! config) config)))'},
 ]),
 patch(app/'test/com/blockether/vis/tui/provider_test.clj',[
  {'from':'73:963','to':'127:5ad','replace':'(defdescribe provider-dialog-save-through-gateway-test\n  (it "hands one preset id and endpoint to the daemon-owned provider route"\n      (let [saved (atom nil)\n            item {:id :ollama :base-url "http://localhost:11434" :models [{:name "qwen"}]}]\n        (with-redefs [vis/gateway-add-provider! #(reset! saved [%1 %2])]\n          (expect (= item (@#\'provider/save-provider-config! item)))\n          (expect (= [:ollama "http://localhost:11434"] @saved))))))'},
  {'from':'1255:4b0','to':'1257:f82','replace':'                      #\'provider/save-provider-config! (fn [config]\n                                                          (reset! saved config)\n                                                          true)'},
  {'from':'1292:878','to':'1294:a64','replace':'        ;; …and the provider really is added, with the model just picked.\n        (expect (= {:id :ollama :models [{:name "acme-1"}] :base-url "http://localhost:11434"}\n                   saved)))'},
 ])
print('\n'.join(map(str,results)))