source_edit = await patch(root / "src/com/blockether/vis/internal/loop.clj", [
    {"from": "4627:0ea", "to": "4628:fb9", "replace": """(defn- ask-code-with-session!
  \"Keep one opaque Svar session per effective Codex router; other providers stay one-shot.\"""},
    {"from": "4647:d79", "to": "4648:d70", "replace": """              current
              (when (and (= provider (:provider entry)) (= router (:router entry))) entry)"""},
    {"from": "6351:af5", "to": "6357:1b8", "replace": """   Router health, budget and retry state are preserved by sharing the original
   map. Stateful session lifecycle compares the effective router snapshots by value,
   so repeated hydration with the same token, endpoint, and headers keeps its opaque
   Svar handle. A changed credential or route produces a different snapshot and
   replaces that handle. A provider token lookup failure is deliberately failure-safe:
   that provider retains its previous snapshot so normal request/error handling remains
   authoritative.\"""}
])
print(source_edit)