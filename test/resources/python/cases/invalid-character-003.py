r = await try_patch(PXT, [
 {"from":"1463:1b5","to":"1466:e61","replace":
'''(def ^:private popen-probe-py
  "Issue #142's own reproduction as an extension: start a child, hand the pid
   the handle carries straight back to the host."
  "import subprocess\\nimport vis\\ndef probe():\\n    '''await probe() -> {'pid'} — start a child and report the handle it got.'''\\n    child = subprocess.Popen(['/bin/sleep', '39'])\\n    return {'pid': child.pid, 'poll': child.poll()}\\nvis.extension(name='popen-probe', description='popen probe', alias='popen', symbols=[vis.symbol(probe, tag='observation')])")'''},
 {"from":"1478:c5d","to":"1500:ca3","replace":
'''  ;; Regression, issue #142: through this same loader, `Popen(...)` started a real
  ;; child and handed the extension a handle whose pid was `1` — the interpreter's
  ;; own first child SLOT, and 1 is init — so nothing could ps, lsof or supervise
  ;; the child the extension had just started.
  (it "hands a tool the real OS pid of the child its Popen started"
      (with-loaded
        {"popen_probe.py" popen-probe-py}
        (fn [_ _]
          (let [result
                ((symbol-fn (registered "popen-probe") 'probe))

                pid
                (long (get-in result [:result "pid"]))

                found
                (ProcessHandle/of pid)]

            (try (expect (extension/envelope-success? result))'''},
])
print(r)
print(cat(PXT, 1476, 1500))