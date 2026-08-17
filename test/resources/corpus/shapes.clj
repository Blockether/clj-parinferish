(ns corpus.shapes
  (:require [clojure.string :as str])
  (:import (java.io File)))

(def config
  {:name    "shapes"
   :tags    #{:a :b :c}
   :matrix  [[1 2 3]
             [4 5 6]]
   :nested  {:deep {:deeper {:deepest [{:k 'quoted-symbol}
                                       {:k `syntax-quoted}]}}}
   :fn      (fn [x] (-> x inc dec))
   :meta    ^{:doc "meta map"} [1 2]
   :file    (File. "x")})

#?(:clj  (defn platform [] :jvm)
   :cljs (defn platform [] :js))

(defn ^:private transform
  [{:keys [a b] :or {a 1 b 2} :as m}]
  (let [f #(* % %)
        g (partial + a)]
    (->> (range 10)
         (map f)
         (filter odd?)
         (reduce g)
         (assoc m :result))))

(def deep
  (((((((((identity identity) identity) identity) identity)
   identity) identity) identity) identity) str/join))
