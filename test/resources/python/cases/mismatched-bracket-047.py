r_eng = patch(eng, [{"from": "1114:d4c", "replace": """  (live-node invalid-live-view! node))

(defn live-nodes?
  "Whether `nodes` are the picture a human WATCHES rather than the questions a
   form asks. A layout group is the ONE node both vocabularies share, so a
   builder composing one asks its children which check it is dated against — and
   a group inside a group answers by its own children."
  [nodes]
  (boolean (some (fn [node]
                   (when (map? node)
                     (if (group-node? node)
                       (live-nodes? (pick* node :fields))
                       (contains? hi-spec/live-node-types
                                  (some-> (trimmed (pick* node :type)) str/lower-case)))))
                 nodes)))""")])
print(str(r_eng)[:400])