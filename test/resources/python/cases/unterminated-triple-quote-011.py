spec_patch = await patch(root / "src/com/blockether/vis/internal/view/spec.clj", [
 {"from":"2:1e3", "to":"25:63f", "replace":'''  "The executable contract for every View document.

   Two temporal kinds share this vocabulary. An `:input` View is a typed form with
   an answer contract; a `:live` View is a semantic picture changed by patches. Both
   use the same group/layout language, lifecycle envelope and CLOSED-map rule.

   [[com.blockether.vis.internal.view]] PARSES extension data into one normalized
   shape and refuses unknown names or keys. This namespace DECLARES that shape with
   `clojure.spec`: input fields and answers, live nodes and patches, and the complete
   roots every renderer receives. A declared key is therefore part of the contract,
   not optional metadata a normalizer may silently discard.

   The functions here only EXPLAIN invalid values; the View engine owns the error
   envelopes and checks the five boundary seams once, never per keystroke."''},
 {"from":"31:94b", "replace":''';; The closed vocabulary

(def view-kinds
  "Wire name -> lifecycle kind. Capability policy dispatches on this CLOSED set."
  {"input" :input
   "live" :live})'''},
 {"from":"358:b7c", "replace":'''  {:view-kinds (vec (sort (keys view-kinds)))
   :field-types (vec (sort (keys field-types)))'''}
])
print(spec_patch)