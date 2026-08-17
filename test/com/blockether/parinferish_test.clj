(ns com.blockether.parinferish-test
  (:require [clojure.string :as str]
            [clojure.test :refer [deftest is testing]]
            [com.blockether.parinferish :as pf])
  (:import (com.blockether.parinferish Parinfer Parinfer$Mode)))

;; ── indent mode: the indentation is the truth ────────────────────────────────

(deftest closes-the-form-the-indentation-ended
  (is (= "(defn f [x]\n  (inc x))"
         (pf/repair "(defn f [x]\n  (inc x)" {:mode :indent})))
  (testing "the closer lands on the last line that belonged to the form"
    (is (= "(let [a 1]\n  (println a))\n\n(def b 2)\n"
           (pf/repair "(let [a 1]\n  (println a)\n\n(def b 2)\n" {:mode :indent})))))

(deftest closes-with-the-delimiter-that-was-opened
  (is (= "[1 2 3]\n" (pf/repair "[1 2 3\n" {:mode :indent})))
  (is (= "{:a 1}\n" (pf/repair "{:a 1\n" {:mode :indent})))
  (is (= "#{1 2}\n" (pf/repair "#{1 2\n" {:mode :indent}))))

(deftest moves-a-closer-down-past-the-lines-it-orphaned
  ;; the deeper lines belong INSIDE the form, so the closer travels to their end
  (is (= "(do (a)\n    (b))\n" (pf/repair "(do (a))\n    (b)\n" {:mode :indent}))))

(deftest drops-a-surplus-closer
  (is (= "(a b)\n" (pf/repair "(a b))\n" {:mode :indent})))
  (testing "and a closer of the wrong kind"
    (is (= "(a b)\n" (pf/repair "(a ]b)\n" {:mode :indent})))))

(deftest leaves-balanced-code-byte-for-byte-alone
  (let [src "(ns app.core)\n\n(defn f\n  \"Doc.\"\n  [x]\n  (let [y (inc x)]\n    {:y y :v [1 2 3]}))\n"]
    (is (= src (pf/repair src {:mode :indent})))
    (is (false? (pf/changed? (pf/parse src {:mode :indent}))))))

(deftest a-delimiter-that-is-not-a-delimiter
  (testing "character literals"
    (is (= "(list \\( \\) \\[)\n" (pf/repair "(list \\( \\) \\[)\n" {:mode :indent}))))
  (testing "inside a string"
    (is (= "(str \"a ( b\")\n" (pf/repair "(str \"a ( b\"\n" {:mode :indent}))))
  (testing "inside a comment"
    (is (= "(f x) ; ) ] }\n" (pf/repair "(f x) ; ) ] }\n" {:mode :indent}))))
  (testing "a multiline string carries its own delimiters"
    (is (= "(def s \"line (\nline )\")\n" (pf/repair "(def s \"line (\nline )\"\n" {:mode :indent})))))

;; ── a source that cannot be read is never rewritten ──────────────────────────

(deftest an-unterminated-string-disables-every-repair
  (let [src "(def s \"open\n(def t 2)\n"]
    (doseq [mode [:indent :paren nil]]
      (is (= src (pf/repair src {:mode mode})) (str "mode " mode)))
    (is (= "Unbalanced quote" (pf/error (pf/parse src {:mode :indent}))))))

(deftest a-line-ending-in-a-backslash-disables-every-repair
  (let [src "(def x \\\n"]
    (is (= src (pf/repair src {:mode :indent})))
    (is (= "Backslash at end of line" (pf/error (pf/parse src {:mode :indent}))))))

;; ── paren mode: the delimiters are the truth ─────────────────────────────────

(deftest paren-mode-pushes-a-line-back-inside-its-form
  ;; one space: the floor is the column right after the collection's opener
  (is (= "(let [a 1]\n (println a))\n"
         (pf/repair "(let [a 1]\n(println a))\n" {:mode :paren}))))

(deftest paren-mode-refuses-a-file-it-cannot-read
  (let [src "(a b))\n(c\n"]
    (is (= src (pf/repair src {:mode :paren})))
    (is (some? (pf/error (pf/parse src {:mode :paren}))))))

;; ── no mode: read only ───────────────────────────────────────────────────────

(deftest reading-without-repairing
  (doseq [[src err] [["(a b)\n" nil]
                     ["(a b\n" "EOF while reading"]
                     ["(a b]\n" "Unmatched delimiter"]
                     ["(a b))\n" "Unmatched delimiter"]]]
    (let [r (pf/parse src nil)]
      (is (= src (pf/flatten r)) src)
      (is (= err (pf/error r)) src))))

;; ── smart mode ───────────────────────────────────────────────────────────────

(deftest smart-mode-splits-the-file-at-the-cursor
  ;; `(a\nb)` is the smallest source the two modes disagree about: indent mode
  ;; closes after `a` and drops the orphaned `)`, paren mode indents `b` inside.
  (let [src "(a\nb)\n"]
    (testing "the form starts AT the cursor, so paren mode owns it"
      (is (= "(a\n b)\n" (pf/repair src {:mode :smart :cursor-line 0 :cursor-column 0}))))
    (testing "the cursor moved one column past the opener: indent mode owns it"
      (is (= "(a)\nb\n" (pf/repair src {:mode :smart :cursor-line 0 :cursor-column 1}))))))

;; ── what the repair did ──────────────────────────────────────────────────────

(deftest edits-name-every-change-in-the-original-coordinates
  (is (= [{:action :insert :offset 21 :line 1 :column 9 :text ")"}]
         (pf/edits (pf/parse "(defn f [x]\n  (inc x)" {:mode :indent}))))
  (is (= [{:action :remove :offset 5 :line 0 :column 5 :text ")"}]
         (pf/edits (pf/parse "(a b))\n" {:mode :indent}))))
  (testing "a closer moved down is one removal and one insertion"
    (is (= [{:action :remove :offset 7 :line 0 :column 7 :text ")"}
            {:action :insert :offset 16 :line 1 :column 7 :text ")"}]
           (pf/edits (pf/parse "(do (a))\n    (b)\n" {:mode :indent})))))
  (testing "nothing to report when nothing changed"
    (is (= [] (pf/edits (pf/parse "(a b)\n" {:mode :indent}))))))

;; ── shape of the input ───────────────────────────────────────────────────────

(deftest handles-every-shape-of-input
  (testing "empty and blank"
    (is (= "" (pf/repair "" {:mode :indent})))
    (is (= "\n\n  \n" (pf/repair "\n\n  \n" {:mode :indent}))))
  (testing "CRLF survives"
    (is (= "(a\r\n b)" (pf/repair "(a\r\n b" {:mode :indent}))))
  (testing "tabs and unicode"
    (is (= "(str \"\u00e6\u00f8\u00e5 \u2192\" \u03bb)" (pf/repair "(str \"\u00e6\u00f8\u00e5 \u2192\" \u03bb" {:mode :indent}))))
  (testing "a form feed is passed through, not a stop sign"
    ;; upstream's tokenizer had no rule for it and silently dropped the rest of
    ;; the file; here it is one more character the repair carries along.
    (is (= "(a \f b)" (pf/repair "(a \f b" {:mode :indent}))))
  (testing "no trailing newline"
    (is (= "(a b)" (pf/repair "(a b" {:mode :indent})))))

(deftest nesting-deeper-than-any-real-file
  (let [depth 400
        src (str (str/join (repeat depth "(")) "x")]
    (is (= (str src (str/join (repeat depth ")"))) (pf/repair src {:mode :indent})))))

;; ── the Java API is the library; the Clojure one is a facade ─────────────────

(deftest java-entry-points
  (is (= "(a b)" (Parinfer/indentMode "(a b")))
  (is (= "(a\n b)" (Parinfer/parenMode "(a\nb)")))
  (is (= "(a b)" (Parinfer/smartMode "(a b" 99 0)))
  (is (= "(a b" (.text (Parinfer/parse "(a b" Parinfer$Mode/NONE))))
  (is (thrown? IllegalArgumentException (Parinfer/parse "(a b" Parinfer$Mode/SMART)))
  (is (thrown? NullPointerException (Parinfer/indentMode nil))))

(deftest unknown-mode-is-refused-by-name
  (is (thrown-with-msg? clojure.lang.ExceptionInfo #"Unknown parinfer mode"
                        (pf/repair "(a" {:mode :indentish}))))

;; ── the whole point: cost is linear in the file ──────────────────────────────

(deftest repairs-a-large-file-in-milliseconds
  ;; The rewrite exists because upstream was quadratic: this file took it minutes.
  ;; The budget is deliberately loose (a slow shared runner is still 100x under it);
  ;; it only has to fail if the cost ever becomes quadratic again.
  (let [form "(defn handler-%d [request]\n  (let [body (:body request)]\n    {:status 200 :body body}))\n\n"
        src (str/join (map #(format form %) (range 5000)))
        _ (pf/repair src {:mode :indent})              ; warm
        broken (str/replace src "{:status 200 :body body}))" "{:status 200 :body body})")
        start (System/nanoTime)
        out (pf/repair broken {:mode :indent})
        ms (/ (- (System/nanoTime) start) 1e6)]
    (is (= 19999 (count (str/split-lines src))) "twenty thousand lines of it")
    (is (= src out) "every one of the 5000 forms is closed again")
    (is (< ms 3000) (format "20 000 lines took %.0f ms" ms))
    (println (format "  20 000 lines repaired in %.1f ms" ms))))
