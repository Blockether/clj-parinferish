print(patch(project_root_path / 'src/com/blockether/vis/internal/foundation/shell.clj', [
{'from':'79:5c0','replace':'  (:import (java.io File)\n           (java.nio.file Files LinkOption)\n           (java.nio.file.attribute BasicFileAttributes)\n           (java.util LinkedHashMap)'},
{'from':'395:000','replace':r'''
(defn- terminal-mode
  "Finite ANSI/VT state; :visible emits this character and returns to plain text."
  [mode c]
  (case mode
    :osc (case c \u0007 :plain \u001b :osc-escape :osc)
    :osc-escape (case c \\ :plain \u0007 :plain \u001b :osc-escape :osc)
    :escape (cond (= c \[) :csi
                  (= c \]) :osc
                  (<= 0x20 (int c) 0x2f) :escape-intermediate
                  (<= 0x30 (int c) 0x7e) :plain
                  :else (terminal-mode :plain c))
    :escape-intermediate (cond (<= 0x20 (int c) 0x2f) :escape-intermediate
                               (<= 0x30 (int c) 0x7e) :plain
                               :else (terminal-mode :plain c))
    :csi (cond (<= 0x30 (int c) 0x3f) :csi
               (<= 0x20 (int c) 0x2f) :csi-intermediate
               (<= 0x40 (int c) 0x7e) :plain
               :else (terminal-mode :plain c))
    :csi-intermediate (cond (<= 0x20 (int c) 0x2f) :csi-intermediate
                            (<= 0x40 (int c) 0x7e) :plain
                            :else (terminal-mode :plain c))
    (case c \u001b :escape \u009b :csi :visible)))

(defn- terminal-chunk
  "Strip escapes without retaining an OSC payload, even across byte windows."
  [mode ^String text emit?]
  (let [out (when emit? (StringBuilder.))]
    (loop [i 0 mode mode]
      (if (= i (.length text))
        {:mode mode :text (when out (.toString out))}
        (let [c (.charAt text i)
              next-mode (terminal-mode mode c)
              visible? (= :visible next-mode)]
          (when (and out visible?) (.append out c))
          (recur (inc i) (if visible? :plain next-mode)))))))

(defonce ^:private ^LinkedHashMap terminal-checkpoints (LinkedHashMap. 256 (float 0.75) true))

(defn- terminal-log-text
  "Normalize a raw log window without sharing a reader cursor. The bounded cache
   holds only parser modes, never output. A cold/random read replays its prefix
   in bounded chunks; following next_offset reuses the preceding checkpoint.
   Active logs use the spawn's exit atom as a generation token. Retired files
   use filesystem identity and revision, so replacement cannot reuse old state."
  [id ^File file entry {:keys [offset next-offset text]}]
  (if (empty? text)
    ""
    (let [attrs (Files/readAttributes (.toPath file) BasicFileAttributes (make-array LinkOption 0))
          generation [(.getPath file) (.fileKey attrs) (.creationTime attrs)
                      (or (:exit entry) [(.size attrs) (.lastModifiedTime attrs)])]
          key [generation offset]
          mode (or (locking terminal-checkpoints (.get terminal-checkpoints key))
                   (loop [at 0 mode :plain]
                     (if (>= at offset)
                       mode
                       (let [chunk (shell-log/read-chunk
                                     id file {:offset at :limit (min shell-log/default-chunk-bytes
                                                                    (- offset at))})
                             next-at (:next-offset chunk)]
                         (when (<= next-at at)
                           (throw (ex-info "Shell log changed while reading terminal context."
                                           {:id id :offset offset :at at})))
                         (recur next-at (:mode (terminal-chunk mode (:text chunk) false)))))))
          result (terminal-chunk mode text true)]
      (locking terminal-checkpoints
        (.put terminal-checkpoints key mode)
        (.put terminal-checkpoints [generation next-offset] (:mode result))
        (while (> (.size terminal-checkpoints) 256)
          (.remove terminal-checkpoints (.next (.iterator (.keySet terminal-checkpoints))))))
      (normalize-terminal-output (:text result)))))
'''.replace('\\','\')},
{'from':'2019:58e','to':'2021:3b7','replace':'                     "out" (if (::raw-output? opts)\n                             (:text chunk)\n                             (terminal-log-text id file entry chunk))'}]))
print(await format_code({'language':'clojure','paths':['src/com/blockether/vis/internal/foundation/shell.clj','test/com/blockether/vis/internal/foundation/shell_test.clj']}))