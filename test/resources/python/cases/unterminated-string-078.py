engine_edits = [
 {"from":"2:ba5", "to":"38:76b", "replace":'''  "The one lifecycle for every operator-facing View.

   A View has a CLOSED semantic document, a stable id, and the same `open`, `patch`
   and `close` rail on every channel. Its `:kind` declares the capability policy:

   - `:input` is Human Input — a typed form that BLOCKS until [[submit!]],
     [[cancel!]], timeout, or interruption;
   - `:live` is a non-blocking picture driven by its producer and optionally
     interrupted by the operator.

   The distinction belongs in policy, not transport. Both kinds share the pending
   registry and publish `:view/open` / `:view/patch` / `:view/close` envelopes;
   renderers dispatch on `:kind` and never infer behavior from an event name.

   This namespace PARSES extension data against the CLOSED vocabulary declared by
   [[com.blockether.vis.internal.view.spec]]. Input answers are coerced and checked
   once at the settle seam; live patches are normalized and materialized once before
   any surface sees them. Unknown keys are refused, while every declared key is
   preserved through normalization.

   Secrets never travel as plaintext. A `:password` and an `:otp` field resolve to
   an opaque `vis-secret:<uuid>` handle; plaintext stays in a process-local vault
   and is readable only through [[reveal-secret]] from the trusted extension side."''},
 {"from":"1704:be5", "to":"1708:e69", "replace":'''(defn live-result<-wire
  "Inverse of the wire projection for a view's VERDICT — what a `view.close`
   session event carries."
  [wire]
  (live<-wire-checked "verdict" view-spec/live-result-error wire))''},
 {"from":"1713:dbf", "replace":'''  (transduce (map #(channel-events/publish-channel-event! % event)) + 0 channel-ids))

(defn- lifecycle-event
  "Canonical channel envelope for either View kind."
  [op entry payload]
  (merge {:op op
          :kind (:kind entry)
          :view-id (:id entry)
          :session-id (:session-id entry)}
         payload))''},
 {"from":"1804:690", "to":"1808:eb2", "replace":'''    (when (zero? (long (publish! (:channel-ids entry)
                                  (lifecycle-event :view/open entry {:view view}))))''},
 {"from":"1859:341", "to":"1863:337", "replace":'''        (publish! (:channel-ids entry)
                  (lifecycle-event :view/patch entry {:patch applied}))''},
 {"from":"2124:341", "to":"2128:ebb", "replace":'''               (publish! (:channel-ids entry)
                         (lifecycle-event :view/close entry {:result artifact-result}))''},
 {"from":"2278:d89", "to":"2284:a1d", "replace":'''      ;; The lifecycle envelope carries `:session-id` from the removed entry;
      ;; listeners never have to recover routing data from the registry.
      (publish! (:channel-ids entry)
                (lifecycle-event :view/close entry {:result {:reason (:reason result)}}))''},
 {"from":"2394:02c", "replace":"          :kind :input"},
 {"from":"2414:9f3", "to":"2417:09b", "replace":'''    (if (zero? (long (publish! (:channel-ids entry)
                               (lifecycle-event :view/open entry
                                                {:view (request->view entry)}))))''},
]
engine_patch = await patch(root / "src/com/blockether/vis/internal/view.clj", engine_edits)
print(engine_patch)