doc_edit = await patch(str(loop_path), [{
    "from": "11709:e81",
    "to": "11721:88a",
    "replace": """(defn refresh-cached-routers!
  \"Reseat `:router` on every cached env's environment map.

   `create-environment` snapshots the router into
   `(:router env)` at construction time, and the iteration loop calls
   `(svar/ask-code! (:router environment) ...)` - not the global
   `router-atom`. So when a frontend changes provider
   config and rebuilds the global router, every long-lived env in the
   cache (TUI keeps one for the whole session) keeps talking to the
   *previous* model until disposed.

   Provider kickoff hooks run against each session before its new snapshot is
   seated, covering providers added or reconfigured while that session is live.
   A failed kickoff aborts the reseat instead of installing incomplete metadata.
   Call this immediately after `rebuild-router!` so the next `send!` on any cached
   session picks up the new router.\"""}
])
print(doc_edit)