;; The Python repair corpus: `clojure -M:python-corpus` rewrites
;; test/resources/python/expected/ and prints the score and the timing.
(ns python-corpus
  "The Python repair corpus in test/resources/python/.

   `cases/` holds Python blocks from live Vis agent sessions that CPython refused
   to parse, plus `valid-*` blocks that parse and must come back untouched.
   `expected/` holds what the repair does with each case: what CPython said about
   the case, whether the repaired text parses, every fix and problem, and the
   repaired text. `python_test` compares the engine against `expected/`.

   Run `-main` after changing the engine: it rewrites `expected/`, prints what
   got better or worse and how long the repair takes. Review the diff of
   `expected/` and commit it with the change that caused it."
  (:require [clojure.java.io :as io]
            [clojure.string :as str]
            [com.blockether.parinferish.python :as python])
  (:import (java.io File)
           (java.lang ProcessBuilder$Redirect)
           (java.nio.file Files)
           (java.nio.file.attribute FileAttribute)
           (java.util Locale)))

(set! *warn-on-reflection* true)

(def root "test/resources/python")

(defn case-names
  "Every case, sorted: the file names in `cases/` without `.py`."
  []
  (->> (.listFiles (io/file root "cases"))
       (map #(.getName ^File %))
       (filter #(str/ends-with? % ".py"))
       (map #(subs % 0 (- (count %) 3)))
       sort
       vec))

(defn source
  "The text of case `name`."
  ^String [name]
  (slurp (io/file root "cases" (str name ".py")) :encoding "UTF-8"))

(defn expected-file ^File [name] (io/file root "expected" (str name ".txt")))

;; CPython

(defn- python-exe [] (or (System/getenv "PYTHON") "python3"))

(defn- run-python ^String [args]
  (let [pb (doto (ProcessBuilder. ^java.util.List (into [(python-exe)] args))
             (.redirectError ProcessBuilder$Redirect/DISCARD))
        _ (.put (.environment pb) "PYTHONIOENCODING" "utf-8")
        p (.start pb)
        out (slurp (.getInputStream p) :encoding "UTF-8")]
    (when (zero? (.waitFor p)) out)))

(defn cpython?
  "True when a CPython 3.12 or newer answers as `$PYTHON` (default `python3`);
   older versions read f-strings differently."
  []
  (try (= "True" (some-> (run-python ["-c" "import sys; print(sys.version_info >= (3, 12))"]) str/trim))
       (catch java.io.IOException _ false)))

(defn cpython-check
  "Parses `files` with CPython in one process; a vector in the same order of
   `{:ok? true}` or `{:ok? false :line l :column c :message m}`."
  [files]
  (if (empty? files)
    []
    (let [out (run-python (into ["dev/python_check.py"] (map #(.getPath ^File %) files)))]
      (when-not out (throw (ex-info "dev/python_check.py failed" {:files (count files)})))
      (mapv (fn [line]
              (let [[_ status l c m] (str/split line #"\t" 5)]
                (if (= "ok" status)
                  {:ok? true}
                  {:ok? false :line (parse-long l) :column (parse-long c) :message m})))
            (str/split-lines out)))))

(defn- temp-dir ^File []
  (.toFile (Files/createTempDirectory "python-corpus" (make-array FileAttribute 0))))

(defn cpython-check-texts
  "`cpython-check` for strings: writes them to a temporary directory first."
  [texts]
  (let [dir (temp-dir)
        files (vec (map-indexed (fn [i t]
                                  (let [f (io/file dir (format "%04d.py" i))]
                                    (spit f t :encoding "UTF-8")
                                    f))
                                texts))]
    (try (cpython-check files)
         (finally (run! #(.delete ^File %) files) (.delete dir)))))

;; Reports

(defn cpython-line
  "What CPython said about a case, as its report writes it."
  [{:keys [ok? line column message]}]
  (if ok? "ok" (str "line " line ", column " column ": " message)))

(defn error-line
  "The error line a report's `cpython:` line names, or nil for a valid case."
  [cpython]
  (some->> cpython (re-find #"^line (\d+),") second parse-long))

(defn outcome
  "`valid` for a case CPython accepts (the repair must leave it alone), else
   `repaired` when the repaired text parses and `not repaired` when it does not."
  [input-ok? {:keys [changed?]} output-ok?]
  (cond input-ok? (if changed? "valid, but CHANGED" "valid")
        (and changed? output-ok?) "repaired"
        :else "not repaired"))

(defn report
  "The text of an `expected/` file."
  [cpython result-line {:keys [text changed? fixes problems]}]
  (str "cpython: " cpython "\n"
       "result: " result-line "\n"
       (apply str (map #(str "fix: " (:message %) "\n") fixes))
       (apply str (map #(str "problem: " (:message %) "\n") problems))
       (when changed? (str "--- text after repair\n" text))))

(defn read-report
  "The `cpython:` and `result:` lines of `name`'s expected report, or nil."
  [name]
  (let [f (expected-file name)]
    (when (.exists f)
      (let [text (slurp f :encoding "UTF-8")]
        {:text    text
         :cpython (second (re-find #"(?m)^cpython: (.*)$" text))
         :result  (second (re-find #"(?m)^result: (.*)$" text))}))))

;; Timing

(defn- nanos-per-case
  "Median nanoseconds of `runs` repairs of each case, after a warm-up."
  [cases runs]
  (dotimes [_ 20] (run! (fn [[s l]] (python/repair s {:error-line l})) cases))
  (mapv (fn [[s l]]
          (let [ts (sort (repeatedly runs #(let [t (System/nanoTime)]
                                             (python/repair s {:error-line l})
                                             (- (System/nanoTime) t))))]
            (nth ts (quot runs 2))))
        cases))

(defn- percentile [sorted ^double p]
  (nth sorted (min (dec (count sorted)) (long (* p (count sorted))))))

(defn- fmt
  "`format` in the root locale, so the numbers print the same everywhere."
  ^String [pattern & args]
  (String/format Locale/ROOT pattern (to-array args)))

(defn- micros [ns] (fmt "%.0f us" (/ (double ns) 1000.0)))

;; Regeneration

(defn -main
  "Repairs every case, rewrites `expected/`, prints the score, the changes
   against the previous `expected/` and the timing."
  [& _]
  (when-not (cpython?)
    (binding [*out* *err*]
      (println "Needs CPython 3.12 or newer as $PYTHON or python3."))
    (System/exit 1))
  (let [names (case-names)
        inputs (mapv source names)
        in-checks (cpython-check (mapv #(io/file root "cases" (str % ".py")) names))
        results (mapv (fn [s c] (python/repair s {:error-line (:line c)})) inputs in-checks)
        out-checks (cpython-check-texts (map :text results))
        rows (mapv (fn [n c r o]
                     (let [cp (cpython-line c)
                           res (outcome (:ok? c) r (:ok? o))]
                       {:name n :cpython cp :result res :old (read-report n)
                        :report (report cp res r) :problems (count (:problems r))}))
                   names in-checks results out-checks)]
    (.mkdirs (io/file root "expected"))
    (doseq [{:keys [name report]} rows]
      (spit (expected-file name) report :encoding "UTF-8"))
    (let [by (group-by :result rows)
          broken (remove #(str/starts-with? (:result %) "valid") rows)
          unrepaired (get by "not repaired")
          changed (filter #(and (:old %) (not= (:text (:old %)) (:report %))) rows)
          better (filter #(= ["not repaired" "repaired"] [(:result (:old %)) (:result %)]) rows)
          worse (filter #(= ["repaired" "not repaired"] [(:result (:old %)) (:result %)]) rows)
          times (sort (nanos-per-case (mapv (fn [s c] [s (:line c)]) inputs in-checks) 21))]
      (println (fmt "%d cases: %d valid, %d broken" (count rows) (- (count rows) (count broken)) (count broken)))
      (println (fmt "repaired     %d of %d broken (%.1f%%)"
                       (count (get by "repaired")) (count broken)
                       (* 100.0 (/ (count (get by "repaired")) (max 1 (count broken))))))
      (println (fmt "not repaired %d, %d of them with a diagnosis"
                       (count unrepaired) (count (filter #(pos? (long (:problems %))) unrepaired))))
      (println (fmt "valid        %d unchanged, %d CHANGED"
                       (count (get by "valid")) (count (get by "valid, but CHANGED"))))
      (println (fmt "vs expected/: %d reports changed, %d newly repaired, %d no longer repaired"
                       (count changed) (count better) (count worse)))
      (doseq [r worse] (println "  no longer repaired:" (:name r)))
      (println (fmt "time per case: median %s, p90 %s, p99 %s, max %s"
                       (micros (percentile times 0.5)) (micros (percentile times 0.9))
                       (micros (percentile times 0.99)) (micros (last times))))))
  (shutdown-agents))
