results=await gather(
 patch(gw_server,[{"from":"509:d8a","to":"514:3f9","replace":""}]),
 patch(tui_screen,[{"from":"637:e34","to":"645:95d","replace":"        local?\n        (or (nil? session-id) (some? (vis/pending-human-input-request request-id)))\n\n        action\n        (cond-> {:action op}\n          (= :submit op)\n          (assoc :values values))]\n\n    (if local?\n      (vis/view-action! request-id action)\n      (vis/gateway-view-action! session-id request-id action))))"}])
for r in results: print(r)