hashline_test_edit = patch(str(ht), [{
    "from": "67:ca8",
    "to": "109:e73",
    "replace": """(defdescribe
  resolve-one-anchor-write-contract-test
  ;; Regression (session 633cdc58): a line number from one line and a nearby hash
  ;; from another were silently recombined, so patch wrote to the hash's line.
  (it \"an exact line and hash resolve\"
      (expect (= {:from-line 2 :to-line 2}
                 (hashline/resolve-anchor-range content (anchor-of 2) nil))))
  (it \"a hash found one line away is still a mismatch\"
      (let [shifted
            (str \"inserted\\n\" content)

            r
            (hashline/resolve-anchor-range shifted (anchor-of 2) nil)]

        (expect (= :anchor-mismatch (get-in r [:error :reason])))
        (expect (= (hashline/line-anchor 2 \"alpha\") (get-in r [:error :current-anchor])))))
  (it \"a duplicate hash resolves only when it matches the stated line\"
      (let [dupes \"same\\nsame\\nsame\\n\"]
        (expect (= {:from-line 2 :to-line 2}
                   (hashline/resolve-anchor-range dupes (hashline/line-anchor 2 \"same\") nil)))))
  (it \"changed content is a mismatch with the current anchor attached\"
      (let [edited
            \"alpha\\nBETA\\n\\ngamma\\ndelta\\n\"

            r
            (hashline/resolve-anchor-range edited (anchor-of 2) nil)]

        (expect (= :anchor-mismatch (get-in r [:error :reason])))
        (expect (= (hashline/line-anchor 2 \"BETA\") (get-in r [:error :current-anchor])))))
  (it \"a malformed anchor and an out-of-range line are refused on their own terms\"
      (expect (= :anchor-malformed
                 (get-in (hashline/resolve-anchor-range content \"a80\" nil) [:error :reason])))
      (expect (= :anchor-line-out-of-range
                 (get-in (hashline/resolve-anchor-range content \"99:a80\" nil) [:error :reason]))))
  (it \"an inverted span is refused rather than silently reordered\"
      (expect (= :anchor-range-inverted
                 (get-in (hashline/resolve-anchor-range content (anchor-of 4) (anchor-of 2))
                         [:error :reason])))))"""
}, {
    "from": "115:df4",
    "replace": """             (it \"a nearby moved hash follows its content for a read\"
                 (let [shifted (str \"inserted\\n\" content)
                       r (hashline/resolve-anchor-range-read shifted (anchor-of 2) nil)]
                   (expect (= 3 (:from-line r)))
                   (expect (not (:stale? r)))))
             (it \"a stale hash falls back to its line number and says it was stale\""" 
}])
core_test_edit = patch(str(ct), [{
    "from": "1399:e2e",
    "replace": """  ;; Regression (session 633cdc58): a nearby line/hash contradiction relocated
  ;; the write to the hash's line instead of refusing the mixed anchor.
  (it \"a nearby hash mismatch is refused instead of relocating the write\"
      (let [rel
            (write-temp! \"patch/nearby-mismatch.txt\" \"alpha\\nbeta\\ngamma\\n\")

            mixed
            (str \"2:\" (hashline/line-hash \"alpha\"))

            before
            (slurp rel)

            thrown
            (try (patch-span rel mixed nil \"wrong target\")
                 nil
                 (catch clojure.lang.ExceptionInfo e e))]

        (expect (some? thrown))
        (expect (= :anchor-mismatch (:reason (ex-data thrown))))
        (expect (string/includes? (ex-message thrown) \"current anchor at 2\"))
        (expect (= (hashline/line-anchor 2 \"beta\") (:current-anchor (ex-data thrown))))
        (expect (= before (slurp rel)))))
  (it \"an anchor whose content moved far away is refused as misplaced\""" 
}])
print(hashline_test_edit)
print(core_test_edit)