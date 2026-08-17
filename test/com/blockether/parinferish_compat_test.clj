(ns com.blockether.parinferish-compat-test
  "The claim this library makes is that it answers exactly what parinferish 0.8.0
   answers, only in linear time. That claim is checked here against the real
   upstream library, on real files and on thousands of seeded mutations of them —
   a rewrite nobody diffs is a rewrite nobody can trust."
  (:require [clojure.test :refer [deftest is testing]]
            [fuzz]))

(def ^:private corpus
  (delay (fuzz/sources ["src" "test" "dev" "test/resources/corpus"])))

(deftest agrees-with-upstream-on-every-file-in-this-repo
  (let [{:keys [cases bad]} (fuzz/run @corpus {})]
    (is (pos? cases))
    (is (= [] bad) (str "diverged on " (count bad) " of " cases " cases"))))

(deftest agrees-with-upstream-on-broken-files
  (testing "every way an edit breaks a file: dropped, added, moved, truncated"
    (let [{:keys [cases bad]} (fuzz/run @corpus {:seed 20260610 :mutations 400})]
      (is (pos? cases))
      (is (= [] bad) (str "diverged on " (count bad) " of " cases " cases")))))

(deftest agrees-with-upstream-on-the-shapes-that-broke-it-once
  (testing "a closer inserted at the end of a collection whose last child is
            itself a collection ending in whitespace"
    ;; Found by the fuzzer: upstream's `insert-delim` splits the trailing
    ;; whitespace off the collection's OWN children, so it never reaches into the
    ;; child — closing after the child, whitespace and all.
    (let [src "(\n  \"s\"\n\n  (:import (java.io File)\n     "]
      (is (empty? (fuzz/check-every-mode src 5 33))))))
