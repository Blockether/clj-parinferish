(ns corpus.comments)

;; A leading comment ) with a stray closer
;; and another one ]

(defn f
  [x]                    ; trailing comment (
  #_(ignored form)
  (if (pos? x)
    ;; branch comment {
    (do
      (println "positive")

      x)

    (- x)))

(defn g []
  (let [a 1

        b 2]

    ;; a comment alone in a body
    [a b]))
