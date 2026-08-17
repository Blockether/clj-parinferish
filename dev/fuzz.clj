(ns fuzz
  "The differential harness: this library against the REAL parinferish 0.8.0,
   over whole files and over seeded mutations of them.

   The rewrite's whole claim is that it answers exactly what upstream answers,
   only in linear time — so the claim is checked, not asserted. `check-file`
   compares one file in every mode; `mutate` breaks a file the way an editing
   agent breaks one (a dropped closer, a dropped quote, a swapped line, a
   truncation); `run` reports every disagreement it found.

   Test scope: upstream is a `:test`-only dependency and never ships."
  (:require [clojure.java.io :as io]
            [clojure.string :as str]
            [parinferish.core :as upstream])
  (:import (com.blockether.parinferish Parinfer Parinfer$Mode)))

(defn- ours [^String s mode cursor-line cursor-column]
  (case mode
    :indent (Parinfer/indentMode s)
    :paren (Parinfer/parenMode s)
    :smart (Parinfer/smartMode s (int cursor-line) (int cursor-column))
    (.text (Parinfer/parse s Parinfer$Mode/NONE))))

(defn- theirs [s mode cursor-line cursor-column]
  (upstream/flatten
   (upstream/parse s (case mode
                       :smart {:mode :smart :cursor-line cursor-line :cursor-column cursor-column}
                       nil {}
                       {:mode mode}))))

(defn- first-diff [^String a ^String b]
  (let [n (min (count a) (count b))]
    (loop [i 0]
      (cond (= i n) (when (not= (count a) (count b)) i)
            (not= (.charAt a i) (.charAt b i)) i
            :else (recur (inc i))))))

(defn- window [^String s i]
  (subs s (max 0 (- i 50)) (min (count s) (+ i 50))))

(defn check
  "nil when the two implementations agree on `source` in `mode`, else a map
   describing where they part."
  ([source mode] (check source mode 0 0))
  ([source mode cursor-line cursor-column]
   (let [a (theirs source mode cursor-line cursor-column)
         b (ours source mode cursor-line cursor-column)]
     (when (not= a b)
       (let [i (first-diff a b)]
         {:mode mode :cursor [cursor-line cursor-column] :at i
          :upstream (window a i) :ours (window b i) :source source})))))

(defn check-every-mode
  "Every mode, one source. The cursor only matters to smart mode."
  [source cursor-line cursor-column]
  (keep #(check source % cursor-line cursor-column) [:indent :paren :smart nil]))

(defn mutate
  "One source, broken the way an edit breaks one. Returns `[kind source]`, or nil
   when this source has nothing of that kind to break."
  [^java.util.Random r ^String s]
  (let [n (count s)
        ls (vec (str/split-lines s))
        pick (fn [pred] (let [is (vec (for [i (range n) :when (pred (.charAt s i))] i))]
                          (when (seq is) (nth is (.nextInt r (count is))))))
        without (fn [i] (str (subs s 0 i) (subs s (inc i))))]
    (when (and (pos? n) (seq ls))
      (case (.nextInt r 9)
        0 (when-let [i (pick #{\) \] \}})] [:drop-closer (without i)])
        1 (when-let [i (pick #{\( \[ \{})] [:drop-opener (without i)])
        2 (when-let [i (pick #{\"})] [:drop-quote (without i)])
        3 (let [i (.nextInt r n)]
            [:add-closer (str (subs s 0 i) (nth [")" "]" "}"] (.nextInt r 3)) (subs s i))])
        4 (let [i (.nextInt r (count ls))]
            [:drop-line (str/join "\n" (concat (subvec ls 0 i) (subvec ls (inc i))))])
        5 (when (> (count ls) 1)
            (let [i (.nextInt r (dec (count ls)))]
              [:swap-lines (str/join "\n" (assoc ls i (ls (inc i)) (inc i) (ls i)))]))
        6 (let [i (.nextInt r (count ls))
                k (- (.nextInt r 9) 4)
                l (ls i)]
            [:reindent (str/join "\n" (assoc ls i (if (neg? k)
                                                    (subs l (min (count l) (- k)))
                                                    (str (str/join (repeat k " ")) l))))])
        7 [:truncate (subs s 0 (.nextInt r (inc n)))]
        8 (let [i (.nextInt r (count ls))]
            [:insert-block (str/join "\n" (concat (subvec ls 0 i)
                                                  ["(let [a 1" "      b 2]" "  (println a b))"]
                                                  (subvec ls i)))])))))

(defn sources
  "Every Clojure source under `dirs`, as text."
  [dirs]
  (->> dirs
       (mapcat #(file-seq (io/file %)))
       (filter #(.isFile ^java.io.File %))
       (map #(.getPath ^java.io.File %))
       (filter #(re-find #"\.(clj|cljc|cljs|edn)$" %))
       (remove #(re-find #"/(target|\.cpcache|\.git)/" %))
       sort
       (mapv slurp)))

(defn run
  "Compares both implementations on every source and on `mutations` seeded
   mutations of them. Returns `{:cases n :bad [...]}` — `:bad` empty is the
   whole point."
  [texts {:keys [seed mutations] :or {seed 1 mutations 0}}]
  (let [r (java.util.Random. seed)
        whole (mapcat #(check-every-mode % 0 0) texts)
        mutated (when (pos? mutations)
                  (doall
                   (mapcat (fn [_]
                             (let [s (nth texts (.nextInt r (count texts)))]
                               (when-let [[kind m] (mutate r s)]
                                 (map #(assoc % :mutation kind)
                                      (check-every-mode m (.nextInt r 40) (.nextInt r 40))))))
                           (range mutations))))]
    {:cases (+ (* 4 (count texts)) (* 4 mutations))
     :bad (vec (concat whole mutated))}))
