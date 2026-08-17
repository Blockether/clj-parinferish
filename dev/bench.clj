(ns bench
  "The numbers in the README: this library against the real parinferish 0.8.0,
   on files of growing size.

       clojure -M:bench [path ...]

   With no path it grows a synthetic namespace, which is the honest shape for a
   scaling claim: same code, more of it."
  (:require [clojure.string :as str]
            [parinferish.core :as upstream])
  (:import (com.blockether.parinferish Parinfer)))

(defn- ms [^long runs f]
  (dotimes [_ (max 1 (quot runs 2))] (f))                  ; warm
  (let [start (System/nanoTime)]
    (dotimes [_ runs] (f))
    (/ (- (System/nanoTime) start) 1e6 runs)))

(defn- synthetic [forms]
  (str/join (map #(format "(defn handler-%d [request]\n  (let [body (:body request)]\n    {:status 200 :body body}))\n\n" %)
                 (range forms))))

(defn- report [label ^String src]
  (let [lines (count (str/split-lines src))
        broken (str/replace src #"\)\)\n\n$" ")\n\n")
        runs (max 1 (min 20 (quot 200000 (max 1 (count src)))))
        theirs (ms runs #(upstream/flatten (upstream/parse broken {:mode :indent})))
        ours (ms runs #(Parinfer/indentMode broken))]
    (printf "%-24s %7d lines  upstream %9.1f ms  ours %7.2f ms  %6.0fx%n"
            label lines theirs ours (/ theirs (max 0.001 ours)))
    (flush)))

(defn -main [& paths]
  (println "parinferish 0.8.0 vs com.blockether/parinferish, indent mode\n")
  (if (seq paths)
    (doseq [p paths] (report p (slurp p)))
    (doseq [forms [50 250 1000 2500 5000]]
      (report (str forms " forms") (synthetic forms)))))
