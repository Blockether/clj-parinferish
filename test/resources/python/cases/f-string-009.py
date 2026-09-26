samples = {
"a.groovy": 'class Alpha {\n  void a() {}\n\n}\n\n\n\ninterface Beta {\n  int m()\n}\n\n\n\nenum Delta { A, B }\n',
"A.java": 'class Alpha {\n\n  int m() {\n    return 1;\n  }\n\n}\n\nclass Beta {\n}\n',
"a.py": 'class Alpha:\n    def a(self):\n        pass\n\n    def b(self):\n        pass\n\n\n\nclass Beta:\n    pass\n',
"u.py": 'def \u03b1lpha():\n    s = "\ud83d\ude80\u4e2d\u6587"\n    return s\n\n\ndef beta():\n    return "caf\u00e9 na\u00efve"\n',
"a.rs": 'pub mod outer {\n    pub fn inner() {\n    }\n\n}\n\npub fn beta() {}\n',
"a.ex": 'defmodule Alpha do\n  defmacro mac(x) do\n    quote do: unquote(x)\n  end\n\nend\n\ndefmodule Beta do\n  def run, do: :ok\nend\n',
"a.tf": 'resource "aws_s3_bucket" "alpha" {\n  bucket = "x"\n\n}\n\n\n\nvariable "beta" {\n  type = string\n}\n',
"a.graphql": 'type Alpha {\n  n: Int\n\n}\n\n\ntype Beta {\n  m: Int\n}\n',
"a.ts": 'export function alpha() {\n  const s = `a\n\nb`;\n  return s;\n}\n\nexport class Beta {\n\n  m() {}\n\n}\n',
"a.js": 'function alpha() {}\nfunction beta() {}\nclass Delta { m() {} }\n',
"a.rb": 'def alpha\n  <<~TXT\n    a\n\n    b\n  TXT\nend\n\ndef beta\n  2\nend\n',
"a.hcl": 'job "alpha" {\n  group "g" {\n    count = 1\n\n  }\n\n}\n\nservice "beta" {\n  port = 80\n}\n',
"a.yaml": 'alpha:\n  n: 1\n\n\nbeta:\n  m: |\n    text\n\n    more\n\ndelta:\n  k: 3\n',
}
def cs(s): return '"' + s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n') + '"'
bank_clj = "\n".join(f'   {cs(p)} {cs(s)}' for p,s in samples.items())
code = f''';; ---------------------------------------------------------------------------
;; SPAN TORTURE — the property behind the `endLineOf` fix, checked over layouts
;; designed to break it: blank rows before a closing delimiter, several blank
;; rows between definitions, no blank rows at all, nested definitions, heredocs
;; and template literals containing blank lines, unicode, CRLF, a leading gap
;; and a trailing gap.
;; ---------------------------------------------------------------------------

(def ^:private span-torture-bank
  {{
{bank_clj}}})

(defn- torture-variants
  "The same source under layouts that stress trailing-blank-row handling."
  [src]
  {{:plain src
   :trailing-blanks (str src "\\n\\n\\n")
   :leading-blanks (str "\\n\\n" src)
   :wide-gaps (str/replace src "\\n\\n" "\\n\\n\\n\\n")
   :crlf (str/replace src "\\n" "\\r\\n")}})

(defn- torture-rows
  "Definitions with their 1-based start/end lines lifted out of the anchors."
  [path src]
  (let [line #(some-> % (str/split #":") first parse-long)]
    (mapv #(assoc % :start (line (:anchor %)) :end (line (:end-anchor %)))
          (ix/definitions src (ix/detect-language path)))))

(defn- own-text
  "A row's own source, never reaching into the next same-or-shallower row."
  [lines rows i]
  (let [{:keys [start end depth]} (nth rows i)
        cap (or (some (fn [r] (when (<= (:depth r) depth) (dec (:start r)))) (subvec rows (inc i)))
                end)]
    (str/join "\\n" (subvec lines (dec start) (max start (min (count lines) end cap))))))

(defn- span-findings
  "Every way this file's spans could be wrong: a span that runs past EOF, ends on
   a blank row, inverts, overlaps its next sibling or escapes its parent — and,
   the end-to-end property, a replace of a definition with its OWN text that is
   not byte-identical (an overshooting end splices the NEXT definition away)."
  [path src]
  (let [lines (vec (str/split src #"\\n" -1))
        n (count lines)
        rows (torture-rows path src)
        out (atom [])
        bad! (fn [& xs] (swap! out conj (str/join " " (cons path (map str xs)))))]
    (doseq [{:keys [name kind start end]} rows]
      (if-not (and start end)
        (bad! "missing span" name)
        (do (when (> start end) (bad! "start>end" name start end))
            (when (> end n) (bad! "end past EOF" name end n))
            (when (and (<= end n) (str/blank? (nth lines (dec end) "x")))
              (bad! "end line blank" name start end))
            (when (= "other" (str kind)) (bad! "bare other kind" name)))))
    (doseq [[a b] (partition 2 1 rows)]
      (if (> (:depth b) (:depth a))
        (when-not (and (>= (:start b) (:start a)) (<= (:end b) (:end a)))
          (bad! "child escapes parent" (:name a) (:name b)))
        (when (>= (:end a) (:start b))
          (bad! "sibling overlap" (:name a) [(:start a) (:end a)] (:name b) [(:start b) (:end b)]))))
    (let [unique (set (for [[k v] (frequencies (map :name rows))
                            :when (and (= 1 v) (string? k) (seq k) (str/includes? src k))]
                        k))]
      (doseq [i (range (count rows))
              :let [{:keys [name kind]} (nth rows i)]
              :when (unique name)]
        (let [res (try (st/edit-source path src {{:op :replace :target name :kind kind
                                                 :code (own-text lines rows i)}})
                       (catch Exception e (.getMessage e)))]
          (when-not (= res src)
            (bad! "replacing" name "with its own text is not identity —"
                  (first (str/split-lines (str res))))))))
    @out))

(defdescribe span-torture-test
             (it "spans stay inside their own definition across nasty layouts"
                 (let [findings (for [[path src] span-torture-bank
                                      [_ variant] (torture-variants src)
                                      :when (nil? (z/describe-syntax-errors (ix/detect-language path) variant))
                                      f (span-findings path variant)]
                                  f)]
                   (expect (= [] (vec findings)))))
             (it "the identity property really catches a wrong span end"
                 ;; guard the guard: an end one row too long swallows `interface Beta`.
                 (let [src (get span-torture-bank "a.groovy")
                       lines (vec (str/split src #"\\n" -1))
                       overshoot (str/join "\\n" (subvec lines 0 8))]
                   (expect (thrown? Exception
                                    (st/edit-source "a.groovy" src
                                                    {{:op :replace :target "Alpha" :kind "class"
                                                     :code overshoot}}))))))
'''
res = await struct_patch(path="/home/user/vis/test/com/blockether/vis/internal/foundation/editing/tree_sitter_langs_test.clj", op="append", code=code)
print(res[0]["changed"], res[0].get("repaired"), str(res[0]["diff"])[:300])