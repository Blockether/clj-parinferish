(ns com.blockether.parinferish.python-test
  "The Python repair: what its facade answers, the corpus of real slips in
   test/resources/python/ and the bound on its running time."
  (:require [clojure.test :refer [deftest is testing]]
            [com.blockether.parinferish.python :as py]
            [python-corpus :as corpus]))

(defn- summary
  "`repair` of `source`, reduced to the text, the flags and the kinds."
  ([source] (summary source nil))
  ([source opts]
   (let [r (py/repair source opts)]
     {:text     (:text r)
      :changed? (:changed? r)
      :clean?   (:clean? r)
      :fixes    (mapv :kind (:fixes r))
      :problems (mapv :kind (:problems r))})))

(deftest repair-test
  (testing "replaces a closer that closes the wrong bracket"
    (let [r (py/repair "print(len([1, 2)")]
      (is (= "print(len([1, 2]))" (:text r)))
      (is (= [{:kind :close-brackets :line 1 :column 16
               :message "line 1: added ']' at column 16 to close '[' from line 1"}
              {:kind :close-brackets :line 1 :column 17
               :message "line 1: added ')' at column 17 to close '(' from line 1"}]
             (:fixes r)))
      (is (= [{:kind :unclosed-bracket :line 1 :column 6
               :message "line 1, column 6: '(' is never closed"}
              {:kind :mismatched-closer :line 1 :column 16
               :message "line 1, column 16: ')' does not match '[' from line 1, column 11"}]
             (:problems r)))))

  (testing "closes a string at the end of its line"
    (is (= {:text "print(\"hello\")\n" :changed? true :clean? true
            :fixes [:close-quote] :problems [:unclosed-bracket :unterminated-string]}
           (summary "print(\"hello)\n"))))

  (testing "closes a triple-quoted string at the end of the source"
    (is (= {:text "s = \"\"\"abc\nprint(s)\"\"\"\n" :changed? true :clean? true
            :fixes [:close-triple-quote] :problems [:unterminated-triple-string]}
           (summary "s = \"\"\"abc\nprint(s)\n"))))

  (testing "closes brackets left open at the end of the source"
    (is (= {:text "x = foo(1, [2, 3])\n" :changed? true :clean? true
            :fixes [:close-brackets] :problems [:unclosed-bracket :unclosed-bracket]}
           (summary "x = foo(1, [2, 3\n"))))

  (testing "closes the brackets a `;` interrupts"
    (is (= {:text "x = [1, 2]; y = 3\n" :changed? true :clean? true
            :fixes [:close-brackets] :problems [:semicolon-in-brackets]}
           (summary "x = [1, 2; y = 3\n"))))

  (testing "removes a closer nothing opened"
    (is (= {:text "x = 1\n" :changed? true :clean? true
            :fixes [:remove-closer] :problems [:unmatched-closer]}
           (summary "x = 1)\n"))))

  (testing "straightens typographic quotes"
    (is (= {:text "print(\"hi\")\n" :changed? true :clean? true
            :fixes [:straight-quotes] :problems [:typographic-quote :typographic-quote]}
           (summary "print(\u201chi\u201d)\n"))))

  (testing "leaves balanced source alone, even when it is not valid Python"
    (doseq [source ["" "def f(x):\n    return [x, (x + 1)]\n" "x = 1y = 2\n"]]
      (is (= {:text source :changed? false :clean? true :fixes [] :problems []}
             (summary source))
          source))))

(deftest error-line-test
  (let [source "x = foo(1, 2\ny = bar(3))\n"
        repaired {:text "x = foo(1, 2)\ny = bar(3)\n" :changed? true :clean? true
                  :fixes [:close-brackets] :problems [:open-bracket-at-statement]}]
    (testing "without an error line, closes a bracket a new statement shows was left open"
      (is (= repaired (summary source)))
      (is (= "line 1: added ')' at column 13 to close '(' from line 1, and removed the extra ')' on line 2"
             (:message (first (:fixes (py/repair source)))))))
    (testing "with an error line between the bracket and the statement, closes it too"
      (is (= repaired (summary source {:error-line 1})))
      (is (= repaired (summary source {:error-line 2}))))
    (testing "with an error line elsewhere, leaves it alone"
      (is (= {:text source :changed? false :clean? true :fixes [] :problems []}
             (summary source {:error-line 5}))))))

(deftest diagnose-test
  (testing "answers the problems of repair without repairing"
    (doseq [source ["print(len([1, 2)" "print(\"hello)\n" "x = foo(1, 2\ny = bar(3))\n" "x = 1\n"]]
      (is (= (:problems (py/repair source)) (py/diagnose source)) source)))
  (testing "narrows to the error line like repair"
    (is (= [] (py/diagnose "x = foo(1, 2\ny = bar(3))\n" {:error-line 5})))))

;; The corpus

(defn- corpus-rows
  "Every case with its expected report and the repair of its source, given the
   error line CPython reported when the report was written."
  []
  (mapv (fn [name]
          (let [rec (corpus/read-report name)]
            (assoc rec
                   :name name
                   :repair (py/repair (corpus/source name)
                                      {:error-line (corpus/error-line (:cpython rec))}))))
        (corpus/case-names)))

(deftest corpus-test
  (let [rows (corpus-rows)]
    (testing "holds the slips of real sessions, and valid code the repair must leave alone"
      (is (<= 400 (count (remove #(= "ok" (:cpython %)) rows))))
      (is (<= 30 (count (filter #(= "ok" (:cpython %)) rows)))))
    (testing "every case has its report"
      (is (= [] (mapv :name (remove :text rows)))))
    (testing "every case repairs to exactly its report"
      (doseq [{:keys [name text cpython result repair]} rows
              :when text]
        (is (= text (corpus/report cpython result repair)) name)))))

(deftest corpus-cpython-test
  (if-not (corpus/cpython?)
    (println "python-test: no CPython 3.12 or newer; the repaired corpus is not parsed")
    (let [rows (corpus-rows)
          checks (corpus/cpython-check-texts (map (comp :text :repair) rows))]
      (testing "the result line of every report is what CPython says about the repair"
        (doseq [[{:keys [name cpython result repair]} check] (map vector rows checks)]
          (is (= result (corpus/outcome (= "ok" cpython) repair (:ok? check))) name))))))

;; Rescan: the repair scans every candidate by rescanning the text it edited, so a
;; rescan must find exactly what a scan of the whole edited text finds, including
;; where each line left the scan, because the next rescan starts from those.

(def ^:private scanner-class (Class/forName "com.blockether.parinferish.python.Scanner"))

(defn- accessible [^java.lang.reflect.AccessibleObject o]
  (doto o (.setAccessible true)))

(def ^:private scanner-ctor
  (accessible (.getDeclaredConstructor ^Class scanner-class (into-array Class [String]))))

(def ^:private scan-method
  (accessible (.getDeclaredMethod ^Class scanner-class "scan" (into-array Class []))))

(def ^:private rescan-method
  (accessible (.getDeclaredMethod ^Class scanner-class "rescan"
                                  (into-array Class [scanner-class (Class/forName "[C")
                                                     Integer/TYPE Integer/TYPE]))))

(defn- scan [^String text]
  (.invoke ^java.lang.reflect.Method scan-method
           (.newInstance ^java.lang.reflect.Constructor scanner-ctor (object-array [text]))
           (object-array 0)))

(defn- rescan [base ^String text from to]
  (.invoke ^java.lang.reflect.Method rescan-method nil
           (object-array [base (.toCharArray text) (int from) (int to)])))

(def ^:private scanner-fields
  (into {}
        (map (fn [n]
               (let [^java.lang.reflect.Field f (accessible (.getDeclaredField ^Class scanner-class n))]
                 [(keyword n) #(let [v (.get f %)] (if (and v (.isArray (class v))) (vec v) v))])))
        ["n" "lines" "lineStart" "lineDepth" "lineCont" "lineComment" "count" "kind" "pos" "at" "open"
         "suspects" "suspectLine" "suspectOpen" "endsInCode" "lead" "cp" "cps" "stackLog"]))

(defn- scan-state
  "What scanner `x` found, and its checkpoints, as data."
  [x]
  (let [g #((scanner-fields %) x)
        log (g :stackLog)
        firsts (fn [k m] (subvec (g k) 0 (g m)))]
    {:n (g :n)
     :lines (g :lineStart)
     :depth (g :lineDepth)
     :cont (g :lineCont)
     :comment (g :lineComment)
     :problems (mapv vector (firsts :kind :count) (firsts :pos :count) (firsts :at :count)
                     (mapv #(some-> % vec) (firsts :open :count)))
     :suspects (mapv vector (firsts :suspectLine :suspects) (mapv vec (firsts :suspectOpen :suspects)))
     :ends-in-code (g :endsInCode)
     :lead (g :lead)
     :checkpoints (mapv (fn [c]
                          (let [[at line kind depth indent problems suspects stack]
                                (subvec (g :cp) (* 8 c) (* 8 (inc c)))]
                            [at line kind depth indent problems suspects
                             (when-not (neg? stack) (subvec log stack (+ stack depth)))]))
                        (range (g :cps)))}))

(def ^:private edit-snippets
  ["\"" "'" "\"\"\"" "'''" "(" ")" "[" "]" "{" "}" "\n" "\\" "\\\n" "#" ":" ";" "f\"" "f'{" "}'"
   "x" " " "    " "def f():\n" "if x:\n" "\n    " "print(" "\"\"\"\n" "rb'" "» " "“" ""])

(defn- random-edit
  "A seeded edit of `text` as [from to inserted]: up to a few characters, now and then a few lines."
  [^java.util.Random rng ^String text]
  (let [n (count text)
        from (long (case (.nextInt rng 16) 0 0 1 n (.nextInt rng (inc n))))
        del (min (- n from) (if (zero? (.nextInt rng 8)) (.nextInt rng 200) (.nextInt rng 4)))
        ins (apply str (repeatedly (inc (.nextInt rng 2))
                                   #(edit-snippets (.nextInt rng (count edit-snippets)))))]
    [from (+ from del) ins]))

(deftest rescan-test
  (testing "rescanning a chain of edits finds what scanning each edited text finds"
    (let [rng (java.util.Random. 20260527)]
      (doseq [name (corpus/case-names)
              :let [source (corpus/source name)]]
        (loop [base (scan source) text source k 0]
          (when (< k 12)
            (let [[from to ins] (random-edit rng text)
                  edited (str (subs text 0 from) ins (subs text to))
                  x (rescan base edited from to)]
              (is (= (scan-state (scan edited)) (scan-state x)) (pr-str [name k from to ins]))
              (recur x edited (inc k)))))))))

;; Time

(defn- best-nanos
  "The fastest of `runs` timings of `f`: the one the JIT and the collector
   disturbed least."
  [runs f]
  (reduce min (repeatedly runs #(let [t0 (System/nanoTime)] (f) (- (System/nanoTime) t0)))))

(deftest time-test
  (testing "every corpus case repairs in under 10 ms"
    (let [cases (mapv (fn [name]
                        [name (corpus/source name)
                         (corpus/error-line (:cpython (corpus/read-report name)))])
                      (corpus/case-names))]
      (dotimes [_ 5]
        (doseq [[_ s l] cases] (py/repair s {:error-line l})))
      (doseq [[name s l] cases]
        (is (< (best-nanos 3 #(py/repair s {:error-line l})) 10000000) name))))
  (testing "input built to defeat the repair still finishes in under 2 s"
    (doseq [[label unit times] [["open brackets" "(" 200000]
                                ["closers" ")" 200000]
                                ["quotes" "'" 200000]
                                ["unclosed strings" "x = \"abc\n" 50000]
                                ["nested openers" "[{(" 50000]
                                ["mismatched pairs" "(]" 50000]
                                ["unclosed calls" "x = foo(1,\n" 20000]
                                ["triple quotes" "'''a\n" 20000]
                                ["semicolons" "f(a; b)\n" 20000]
                                ["f-strings" "f'{x'\n" 20000]
                                ["backslashes" "a \\ b\n" 50000]]]
      (let [s (apply str (repeat times unit))]
        (py/repair s)
        (is (< (best-nanos 2 #(py/repair s)) 2000000000) label)))))
