te = [
 {"from": "5476:3b1", "replace": '        (expect (str/includes? text "─ 3 more lines ─")\n                "a clipped patch says how much it kept back, in the one rule both surfaces draw")'},
 {"from": "5492:05b", "replace": '''        ;; Regression, user report ("every show-more must be a rule with the words in
        ;; it, not a bigger chevron and `+2 more read files`"): the fold count wore a
        ;; disclosure chevron and a `+N` it had invented for itself.
        (expect (some #(str/includes? % "─ show 1 more file ─") lines)
                "and the count says what it folded, as a rule with the words in it")
        (expect (not-any? #(and (str/includes? % "more file") (str/includes? % "\\u25b8")) lines)
                "a rule is not a disclosure: no chevron stands on the count")''')'''.replace("')","")},
]
print(te[1]["replace"][-200:])
