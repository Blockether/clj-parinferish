;; Python repair — the same idea as parinfer, for the slips a language model makes
;; in Python: quotes and brackets that do not balance. See README.md.
(ns com.blockether.parinferish.python
  "Repairs Python source whose quotes or brackets do not balance: a string that
   never closes, a bracket closed by the wrong closer or not at all, a `;` inside
   brackets, statements glued together by a lost line break.

       (repair \"print(len([1, 2)\")
       ;; => {:text     \"print(len([1, 2]))\"
       ;;     :changed? true
       ;;     :clean?   true
       ;;     :fixes    [{:kind :close-brackets :line 1 :column 16 :message \"...\"} ...]
       ;;     :problems [{:kind :unclosed-bracket :line 1 :column 6 :message \"...\"} ...]}

   The repair makes the delimiters consistent. It cannot tell whether the result
   is the program that was meant, or even valid Python: parse `:text` before you
   run it, and show `:fixes` to whoever wrote the source. When the repair cannot
   finish, `:problems` describes what is wrong with the original source.

   Every call is bounded by the size of its input: the repair tries a handful of
   edits per problem and stops when its work budget runs out."
  (:import (com.blockether.parinferish.python Repair Repair$Fix Repair$Problem Repair$Result)))

(defn- fix->map [^Repair$Fix f]
  {:kind    (keyword (.kind f))
   :line    (.line f)
   :column  (.column f)
   :message (.message f)})

(defn- problem->map [^Repair$Problem p]
  {:kind    (keyword (.kind p))
   :line    (.line p)
   :column  (.column p)
   :message (.message p)})

(defn repair
  "Repairs the quotes and brackets of Python `source`.

   `:error-line` is the 1-based line where the Python parser reported the
   syntax error, when you have it. It matters when every bracket is closed but
   a statement starts while a bracket from an earlier line is still open: the
   repair then closes that bracket only when the error line lies between the
   bracket and the statement. Without it, the repair closes every such bracket.

   Returns a map of
     `:text`     the repaired source, or `source` itself when nothing changed
     `:changed?` true when `:text` differs from `source`
     `:clean?`   true when no quote or bracket problem is left in `:text`
     `:fixes`    what changed, in order
     `:problems` what is wrong with `source`
   Fixes and problems are maps of `:kind` (a keyword), `:line` and `:column`
   (1-based, in `source`) and `:message`, a sentence for a person."
  ([source] (repair source nil))
  ([^String source {:keys [error-line]}]
   (let [^Repair$Result r (Repair/repair source (int (or error-line 0)))]
     {:text     (.text r)
      :changed? (.changed r)
      :clean?   (.clean r)
      :fixes    (mapv fix->map (.fixes r))
      :problems (mapv problem->map (.problems r))})))

(defn diagnose
  "The quote and bracket problems of Python `source`, without repairing it — the
   `:problems` of `repair`, at a fraction of the cost."
  ([source] (diagnose source nil))
  ([^String source {:keys [error-line]}]
   (mapv problem->map (Repair/diagnose source (int (or error-line 0))))))
