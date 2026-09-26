edit(sh_rel, [
("""                      ;; Unconfined, but the operator's `environment:` declarations still
                      ;; apply: they say where a variable comes from, not who may see it.""",
 """                      ;; Unconfined, but the workspace's `.env` and the operator's
                      ;; `environment:` declarations still apply: they say where a variable
                      ;; comes from, not who may see it."""),
])
edit("src/com/blockether/vis/internal/process_jail.clj", [
("""(defn declared-env
  \"The policy's RESOLVED `environment:` declarations, as string pairs. These are
   the operator's own named variables — the value already came from the source
   the declaration picked (`env:`, `dotenv:`, `keychain:`, `command:`), so the
   jail hands them over verbatim. A [[pre-exec-hijack?]] name is dropped even
   here: it would run code in the UNCONFINED detacher/enforcer hops, so no
   declaration can buy it back.\"""",
 """(defn declared-env
  \"The policy's RESOLVED project environment, as string pairs: the workspace's
   `.env`/`.env.local` with the operator's `environment:` declarations on top
   (`config/child-environment-values`). Every value already came from the source
   that produced it, so the jail hands them over verbatim — a confined child can
   read `.env` out of the workspace it was granted anyway, so withholding those
   values would confine nothing. A [[pre-exec-hijack?]] name is dropped even
   here, whether it came from a declaration or from a project `.env`: it would
   run code in the UNCONFINED detacher/enforcer hops, so nothing can buy it
   back.\"""),
("""(defn jailed-child-env
  \"The COMPLETE environment for a confined child: an allowlist of non-secret
   operator variables, plus the resolved `environment:` declarations the policy
   carries, plus this session's proxy + CA variables. Every API key / token /
   credential the operator happens to have exported is DROPPED — a variable a
   child needs is named in `environment:` — and so is every [[pre-exec-hijack?]]
   name, which would run code in the unconfined detacher/enforcer before the jail
   exists.""",
 """(defn jailed-child-env
  \"The COMPLETE environment for a confined child: an allowlist of non-secret
   operator variables, plus the policy's resolved project environment (the
   workspace's `.env` plus the `environment:` declarations), plus this session's
   proxy + CA variables. Every API key / token / credential the operator happens
   to have exported is DROPPED — an AMBIENT variable a child needs is named in
   `environment:` — and so is every [[pre-exec-hijack?]] name, which would run
   code in the unconfined detacher/enforcer before the jail exists."""),
("""(defn child-env-additions
  \"What an UNCONFINED child gets ON TOP of the inherited environment: the
   resolved `environment:` declarations plus this session's proxy + CA variables.
   The declarations apply whether or not the jail is enabled — `environment:`
   says where a variable comes from, and the jail only decides what ELSE a child
   may keep.\"""",
 """(defn child-env-additions
  \"What an UNCONFINED child gets ON TOP of the inherited host environment: the
   resolved project environment (workspace `.env` + `environment:` declarations)
   plus this session's proxy + CA variables. They apply whether or not the jail
   is enabled — the project says where a variable comes from, and the jail only
   decides what ELSE a child may keep.\"""),
])
