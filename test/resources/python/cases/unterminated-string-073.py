root=Path(session["workspace"]["root"])
p1=patch(root/"src/com/blockether/vis/internal/loop.clj",[
 {"from":"2516:221","to":"2557:409","replace":""},
 {"from":"5008:b4e","to":"5008:b4e","replace":"          api-usage (:api-usage ask-result)"},
 {"from":"5303:226","to":"5305:12a","replace":"                       ;; Render metadata is optional; `:code` remains the canonical source."}
])
p2=patch(root/"test/com/blockether/vis/internal/loop_test.clj",[
 {"from":"76:4cb","to":"76:4cb","replace":""},
 {"from":"3035:ca8","to":"3053:0cd","replace":"(defdescribe
  token-cost-test"}
])
print(p1)
print(p2)