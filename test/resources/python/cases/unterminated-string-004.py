results=await gather(patch(p,[{'from':'1085:486','to':'1087:afa','replace':'''            (p/set-colors! g
                           (if (and (= :project-group kind) (not focused?))
                             (t/group-ink (:color entry))
                             t/dialog-fg)
                           t/dialog-bg)'''},{'from':'1129:99d','replace':'                                  (cond (and (= :project-group kind) (not focused?))
                                        (t/group-ink (:color entry))'}]),patch(tp,[{'from':'1134:37a','to':'1137:5cb','replace':'''              (doseq [[label fg] [[:text theme/dialog-fg]
                                  [:hint theme/dialog-hint-key]
                                  [:warning theme/warning-fg]]]'''},{'from':'1869:127','to':'1870:cf9','replace':'''        (is (every? #(= highlight (get-in capture [:frames 0 % 1 :bg]))
                    (range row (+ row height))))
        (when (= :project-group (:kind hit))
          (is (= (#'theme-test/rgb-tuple theme/dialog-fg)
                 (get-in capture [:frames 0 row 6 :fg])))
          (is (= (#'theme-test/rgb-tuple (theme/group-ink "violet"))
                 (get-in capture [:frames 0 row 1 :fg])))))'''}])); print(*results,sep='\n')