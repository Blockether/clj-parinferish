sim = Path(tempfile.mkdtemp(prefix='vis_resume_sim_', dir=str(root/'target'))
sim_work=sim/'work'; sim_work.mkdir(); (sim_work/'README.md').write_text('# Stable\n')
sim_db=sim/'vis.mdb'
init=await shell("git init -q . && git config user.email t@t.co && git config user.name t && git add -A && git commit -qm init",cwd=str(sim_work)); await init.wait(20)
code_a=r'''(do
(require '[com.blockether.vis.internal.loop :as lp]
         '[com.blockether.vis.internal.prompt :as prompt]
         '[com.blockether.vis.internal.extension :as extension]
         '[com.blockether.vis.internal.persistance :as p]
         '[com.blockether.vis.internal.util :as util])
(let [env (lp/create-environment ::router {:db "%s" :channel :cli})]
 (try
  (extension/with-context {:env env}
   (let [standing {:block "<context>fixed</context>" :baseline {}}
         _ (reset! (:standing-ctx-atom env) standing)
         active (prompt/active-extensions env)
         stable (prompt/assemble-stable-prompt-messages env {:system-prompt nil :active-extensions active :session-context (:block standing)})
         messages (conj stable {:role "user" :content "turn one"})
         entry {:messages messages :weights (vec (repeat (count messages) 10)) :input-tokens 1000 :at-ms (util/now-ms)
                :completed-turn {:turn-position 1 :summaries nil :stable-message-count (count stable)
                                 :assistant-message {:role "assistant" :content "done"}}}]
    (p/db-set-session-prompt-cache-state! (:db-info env) (:session/state-id env)
                                          {:route [:zai-coding-plan "glm-5.3-flash"] :entry entry :standing-ctx standing})
    (prn {:session-id (:session-id env) :stable-count (count stable)})))
  (finally (lp/dispose-environment! env)))))''' % str(sim_db)
ha=await shell("clojure -J-Duser.dir=%s -M -e %s" % (shlex.quote(str(sim_work)), shlex.quote(code_a)),cwd=str(root)); ra=await ha.wait(180)
print({'exit':ra.get('exit'),'out':ra.get('out','')[-1200:]})