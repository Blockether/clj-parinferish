state_revert = patch(root / "src/com/blockether/vis/internal/gateway/state.clj", [
    {"from": "15:2d7", "to": "17:c7f", "replace": "  (:require [clojure.string :as str]\n            [com.blockether.vis.internal.attachment-storage :as attachment-storage]"},
    {"from": "397:214", "to": "402:84c", "replace": "  ([sid type payload] (append-event! sid type payload {:store? true}))\n  ([sid type payload {:keys [store?]}]\n   (let [captured"}
])
test_revert = patch(root / "test/com/blockether/vis/contract/gateway_test.clj", [
    {"from": "5:b29", "to": "6:acf", "replace": "            [com.blockether.vis.internal.gateway.server :as server]"},
    {"from": "9:69f", "replace": "            [lazytest.core :refer [defdescribe expect it]]"},
    {"from": "45:150", "to": "51:0ca", "replace": "      (expect (= contract/view-events\n                 {:open gateway-view/view-open-event\n                  :patch gateway-view/view-patch-event\n                  :close gateway-view/view-close-event}))))"
])
print("STATE", state_revert, "\nTEST", test_revert)