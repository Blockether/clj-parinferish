sh_install=await shell("VERSION=0.7.153 clojure -T:build install",cwd=str(svar_root))
install=await sh_install.wait(120)
print("INSTALL",install.get("status"),(install.get("out") or "")[-1000:])
sh_verify=await shell("./verify.sh",cwd=str(svar_root))
r1,r2=await gather(
 run_tests({"language":"clojure","paths":[str(tf)]}),
 run_tests({"language":"clojure","paths":["test/com/blockether/vis/internal/loop_test.clj::emergency-context-fold-projection-test"]})
vr=await sh_verify.wait(300)
print("COMPACTION",r1.get("is_pass"),r1.get("total"),r1.get("failures")); print((r1.get("output") or "")[-1000:])
print("OVERFLOW",r2.get("is_pass"),r2.get("total"),r2.get("failures")); print((r2.get("output") or "")[-1200:])
print("VERIFY",vr.get("status")); print((vr.get("out") or "")[-4000:])