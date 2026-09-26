toml_block = r'''(defn- toml-literal-at?
  "Does `lit` start at index `i` of `s`?"
  [^String s ^long i ^String lit]
  (and (<= (+ i (.length lit)) (.length s)) (.startsWith s lit (int i))))

(defn- toml-skip-line
  "Index of the first character after the line holding index `i` of `s`."
  [^String s ^long i]
  (let [j (.indexOf s "\n" (int i))]
    (if (neg? j) (.length s) (inc j))))

(defn- toml-skip-past
  "Index just past the first `close` at or after `from` in `s`, or the end of `s`
   when it never closes. With `escapes?` a backslash consumes the character behind
   it, the way a TOML basic string escapes its own quote."
  [^String s ^long from ^String close escapes?]
  (let [n (.length s)]
    (loop [i from]
      (cond (>= i n) n
            (and escapes? (= \\ (.charAt s (int i)))) (recur (+ i 2))
            (toml-literal-at? s i close) (+ i (.length close))
            :else (recur (inc i))))))

(defn- toml-header-at
  "The TOML table header opening at index `i` of `s` (the index of its `[`), as
   [path end]: the dotted path — nil when the brackets never close on that line —
   and the index just past what was read. Quoted key segments are unquoted and keep
   their own dots, so [\"a.b\"] is the single key `a.b`."
  [^String s ^long i]
  (let [n (.length s)

        start
        (if (toml-literal-at? s i "[[") (+ i 2) (inc i))]

    (loop [j
           start

           seg
           ""

           segs
           []]

      (if (>= j n)
        [nil n]
        (let [c (.charAt s (int j))]
          (cond (= c \newline)
                [nil j]

                (= c \])
                [(let [segs (conj segs (str/trim seg))]
                   (when (every? seq segs) (str/join "." segs)))
                 (if (toml-literal-at? s (inc j) "]") (+ j 2) (inc j))]

                (= c \.)
                (recur (inc j) "" (conj segs (str/trim seg)))

                (or (= c \") (= c \'))
                (let [e (long (toml-skip-past s (inc j) (str c) (= c \")))]
                  (recur e (str seg (subs s (inc j) (max (inc j) (dec e)))) segs))

                :else
                (recur (inc j) (str seg c) segs)))))))

(defn- toml-table-headers
  "The dotted paths of the TOML TABLE HEADERS `text` declares, in order — `tool.uv`
   for `[tool.uv]`, `tool.uv.index` for `[[tool.uv.index]]`.

   SCANNED in TOML's own lexical states, never as substring soup: line comments,
   basic and literal strings and both multi-line string forms are walked over, so a
   `[tool.uv]` sitting in a comment, in a description string or inside a docstring
   is not a table header. A header has to OPEN its line, and one whose brackets
   never close yields nothing."
  [^String text]
  (let [^String s
        (str text)

        n
        (.length s)]

    (loop [i
           0

           line-start?
           true

           acc
           []]

      (if (>= i n)
        acc
        (let [c (.charAt s (int i))]
          (cond (= c \newline)
                (recur (inc i) true acc)

                (or (= c \space) (= c \tab) (= c \return))
                (recur (inc i) line-start? acc)

                (= c \#)
                (recur (long (toml-skip-line s i)) true acc)

                (toml-literal-at? s i "\"\"\"")
                (recur (long (toml-skip-past s (+ i 3) "\"\"\"" true)) false acc)

                (toml-literal-at? s i "'''")
                (recur (long (toml-skip-past s (+ i 3) "'''" false)) false acc)

                (= c \")
                (recur (long (toml-skip-past s (inc i) "\"" true)) false acc)

                (= c \')
                (recur (long (toml-skip-past s (inc i) "'" false)) false acc)

                (and line-start? (= c \[))
                (let [[path end] (toml-header-at s i)]
                  (recur (long end) false (cond-> acc path (conj path))))

                :else
                (recur (inc i) false acc)))))))'''
Path("/tmp/vis_toml_block.txt").write_text(toml_block)

lines = interp.read_text().split("\n")
new = lines[:6] + ["            [com.blockether.vis.internal.config.core :as config]))"] + lines[8:39] + toml_block.split("\n") + lines[67:]
Path("/tmp/vis_interp_new.txt").write_text("\n".join(new))
sh = await shell(f"cp /tmp/vis_interp_new.txt {interp} && wc -l {interp}")
print(sh.wait(30)["out"])
