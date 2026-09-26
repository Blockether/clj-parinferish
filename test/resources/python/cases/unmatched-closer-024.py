probe = r'''
(require '[com.blockether.vis-python-runtime :as rt])
(defn probe [label code]
  (println label
    (try (rt/eval-str (str "(lambda: (" code "))()")) (catch Exception e (str "REFUSED: " (.getMessage e))))))
(let [{:keys [python-home packages]} (rt/initialize! {})]
  (rt/confine! [python-home packages] [(System/getProperty "java.io.tmpdir")] "the sandbox says no")
  (probe :import-pip   "__import__('pip').__version__")
  (probe :pip-internal "str(__import__('pip._internal.cli.main', fromlist=['main']).main)")
  (probe :pip-run      "__import__('pip').main(['--version'])")
  (probe :subprocess   "str(__import__('subprocess').run(['echo','hi']))")
  (probe :write-pkgs   "open(__import__('os').path.join('""" + "'" + '''"))"))
'''
# simpler: separate write probe
probe = probe.split("(probe :write-pkgs")[0] + ")\n"
Path("/tmp/pipprobe.clj").write_text(probe)
sh = await shell("cd ~/vis-python-runtime && VIS_PYTHON_NATIVE_PATH=$PWD/resources/prebuilds/darwin-arm64 clojure -M /tmp/pipprobe.clj 2>&1 | grep -v WARNING | tail -20")
print(sh.wait(600).logs(-25)["out"])