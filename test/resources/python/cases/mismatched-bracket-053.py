r = await patch(edits=[
 {"path":PT,"from_anchor":A[915],"to_anchor":A[916],"replace":
"""   Returns the provider row WITHOUT the key on success (the daemon holds the
   credential), nil on cancel or failure (dialog already shown)."\""".replace('"\\""','"')},
 {"path":PT,"from_anchor":A[959],"to_anchor":A[960],"replace":
"""              (do (vis/gateway-provider-auth-submit-key! pid flow-id api-key)
                  ;; The DAEMON persisted it. Hand the row back WITHOUT the key:
                  ;; a TUI attached to a REMOTE gateway must never write provider
                  ;; credentials into the config of the machine it happens to run
                  ;; on, and every later fleet write merges onto the persisted
                  ;; entry anyway.
                  (dissoc provider :api-key))))))"""},
])
print(json.dumps(r)[:600])