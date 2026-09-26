await shell(op="stop", id="bgate")
code = '(load-file "build.clj") (try (#\'build/assert-graal-pins!) (println :NO-GATE) (catch Exception e (println "GATE FIRED:") (println (.getMessage e))))'
await shell(id="bgate2", cmd=f"cd ~/vis && cp deps.edn /tmp/deps.bak2 && sed -i '' 's|polyglot {:mvn/version \"25.2.4\"}|polyglot {:mvn/version \"25.1.3\"}|' deps.edn && export JAVA_HOME=$HOME/.sdkman/candidates/java/25.2.4-graalce && export PATH=$JAVA_HOME/bin:$PATH && clojure -A:build -M -e {shlex.quote(code)} 2>&1 | tail -12; cp /tmp/deps.bak2 deps.edn; echo RESTORED")
r = await shell(cmd="sleep 75; echo waited", timeout_secs=110)
l = await shell(op="logs", id="bgate2", n=25)
print("\n".join(l["lines"])[-1500:], "|", l["status"])