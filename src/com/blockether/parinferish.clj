(ns com.blockether.parinferish
  "Parinfer for Clojure source — a pure-Java rewrite of parinferish 0.8.0 that is
   linear in the size of the file instead of quadratic.

   `repair` is the whole library: source in, repaired source out.

       (repair \"(defn f [x]\\n  (inc x)\" {:mode :indent})
       ;; => \"(defn f [x]\\n  (inc x))\"

   `parse` returns the result object when you also want the errors or the exact
   edits, and `flatten` takes the text back out of it.

   Modes: `:indent` trusts the indentation and moves the delimiters, `:paren`
   trusts the delimiters and moves the indentation, `:smart` uses indent mode for
   the collections that start before the cursor (`:cursor-line`,
   `:cursor-column`, both zero-based) and paren mode for the rest, and `nil` only
   reads — it repairs nothing and just reports `error`.

   A source whose strings do not terminate, or that ends a line on a backslash,
   comes back verbatim in every mode: a file this library cannot read is a file
   it must not rewrite."
  (:refer-clojure :exclude [flatten])
  (:import (com.blockether.parinferish Parinfer Parinfer$Edit Parinfer$Edit$Action Parinfer$Mode Parinfer$Result)))

(def ^:private modes
  {:indent Parinfer$Mode/INDENT
   :paren  Parinfer$Mode/PAREN
   :smart  Parinfer$Mode/SMART
   nil     Parinfer$Mode/NONE})

(defn- mode-of ^Parinfer$Mode [mode]
  (or (get modes mode)
      (throw (ex-info (str "Unknown parinfer mode: " (pr-str mode))
                      {:mode mode :known (-> modes keys set)}))))

(defn parse
  "Reads `source`, applying the repair named by `:mode`. Returns a
   `com.blockether.parinferish.Parinfer$Result`: `flatten` it for the text,
   `edits` it for the changes, `error` it for the reason it could not read."
  (^Parinfer$Result [source] (parse source nil))
  (^Parinfer$Result [^String source {:keys [mode cursor-line cursor-column]}]
   (let [m (mode-of mode)]
     (if (identical? Parinfer$Mode/SMART m)
       (Parinfer/parse source m (int (or cursor-line 0)) (int (or cursor-column 0)))
       (Parinfer/parse source m)))))

(defn flatten
  "The repaired text of a `parse` result."
  ^String [^Parinfer$Result result]
  (.text result))

(defn repair
  "Repairs `source` and returns the text — `(-> source (parse opts) flatten)`."
  (^String [source] (repair source nil))
  (^String [source opts] (flatten (parse source opts))))

(defn changed?
  "True when the repair changed anything."
  [^Parinfer$Result result]
  (.isChanged result))

(defn error
  "The last problem the read found, or nil: `\"Unbalanced quote\"`,
   `\"Backslash at end of line\"`, `\"Unmatched delimiter\"`, `\"EOF while reading\"`."
  [^Parinfer$Result result]
  (.errorMessage result))

(defn edits
  "What the repair did, in output order: maps of `:action` (`:insert`/`:remove`),
   `:offset`, `:line`, `:column` (all zero-based, in the ORIGINAL source) and
   `:text`."
  [^Parinfer$Result result]
  (mapv (fn [^Parinfer$Edit e]
          {:action (if (identical? Parinfer$Edit$Action/INSERT (.action e)) :insert :remove)
           :offset (.offset e)
           :line   (.line e)
           :column (.column e)
           :text   (.text e)})
        (.edits result)))
