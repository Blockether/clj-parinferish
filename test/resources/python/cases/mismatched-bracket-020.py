goal_detail_src=git_initial_bytes['apps/vis-tui/src/com/blockether/vis/tui/header.clj'].decode().splitlines()
goal_detail_code='\n'.join(goal_detail_src[214:233])
footer_new=goal_detail_code+'''

(defn limits-detail-lines
  "Provider quota summary and reset windows from the current session's cached report."
  [db now-ms]
  (let [provider (session-effective-provider db)
        report (provider-report db provider)]
    (into [(or (when provider (generic-limits-footer-text db provider now-ms))
               "No limits reported by this provider.")]
          (for [row (get-in report [:dynamic :limits])
                :when (get-in row [:window :resets-at-ms])]
            (format-generic-limit-rows now-ms [row])))))

(defn- build-limits-segments
  [db _now-ms]
  (into (cond-> [{:text " Limits " :kind :footer-limits :region :left :priority 1}]
          (get-in db [:session :goal])
          (conj {:text (str " Goal: "
                           (get gateway-contract/session-goal-labels
                                (get-in db [:session :goal "status"])) " ")
                 :kind :footer-goal :region :left :priority 1 :join-left? true}))
        (build-usage-segments db)))'''
print(grep({'query':['defn- provider-report'], 'paths':[str(project_root_path / 'apps/vis-tui/src/com/blockether/vis/tui/footer.clj')], 'context':0}))
print(patch(project_root_path / 'apps/vis-tui/src/com/blockether/vis/tui/footer.clj',[
{'from':'38:651','replace':'            [com.blockether.vis.contract.gateway :as gateway-contract]\n            [com.blockether.vis.tui.client :as lp]'},
{'from':'618:852','to':'635:ccb','replace':footer_new}]))
print(patch(project_root_path / 'apps/vis-tui/src/com/blockether/vis/tui/screen.clj',[
{'from':'3223:985','replace':'  #{:copy-id :workspace-entry :header-help :footer-goal :footer-limits :header-tasks :header-search'},
* [{'from':a,'to':b,'replace':'''                                 :footer-goal
                                 (dlg/text-view-dialog! screen "Session goal"
                                   (footer/goal-detail-lines (get-in @state/app-db [:session :goal])))

                                 :footer-limits
                                 (dlg/text-view-dialog! screen "Limits"
                                   (footer/limits-detail-lines @state/app-db (System/currentTimeMillis)))'''} for a,b in [('6222:5d9','6227:6f0'),('6500:5d9','6504:dfc'),('6631:5d9','6635:dfc')]]))
print(cat(project_root_path / 'apps/vis-tui/test/com/blockether/vis/tui/footer_test.clj',350,377))