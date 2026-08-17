(ns corpus.strings-and-chars
  "Every way a delimiter can appear without being one.")

(def opener \()
(def closer \))
(def bracket \[)
(def brace \{)
(def backslash \\)
(def newline-char \newline)

(def sentence
  "A docstring with ( unbalanced ] delimiters { and a \"quoted\" word,
   a second line whose indentation is deep,
and a third that has none at all.")

(def escaped "a \\\" b \\\\ c")

(def pattern #"[(){}\[\]]+")

(defn describe [x]
  ;; a comment with ) and ] and } in it
  (str "value: " x " " \; " " \, " " \# ))

(comment
  (describe (list \( \) \[ \] \{ \}))
  )
