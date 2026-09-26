> 
# --- commit flow ---
src = sub1(src, '''     ((:transient! mini)
       "Commit"
       {:groups
        [{:title "Arguments"
          :items
          [{:key "h" :type :switch :id :no-verify :label "Disable hooks" :arg "--no-verify"}]}
         {:title "Commands"
          :items [{:key "c" :type :action :id :commit :label "Commit staged"}
                  {:key "a" :type :action :id :amend :label "Amend last commit"}]}]}
       (constantly nil))]''',
'''     ((:transient! mini)
       {:title "Commit"
        :groups
        [{:title "Arguments"
          :items
          [{:key "h" :type :switch :id :no-verify :label "Disable hooks" :arg "--no-verify"}]}
         {:title "Commands"
          :items [{:key "c" :type :action :id :commit :label "Commit staged"}
                  {:key "a" :type :action :id :amend :label "Amend last commit"}]}]})]''')

# --- push flow: spec carries title + read-option ---
src = sub1(src, '''     spec
     {:groups [{:title "Arguments" :items arg-items} {:title "Commands" :items push-items}]}

     read-option
     (fn [{:keys [id]} current]
       (when (= id :topic)
         ((:read! mini)
           "Topic:"
           {:initial (or current (when (and branch (not= branch g-branch)) branch) "")})))]

    (when-let [{:keys [action switches options]} ((:transient! mini) "Push" spec read-option)]''',
'''     spec
     {:title "Push"
      :groups [{:title "Arguments" :items arg-items} {:title "Commands" :items push-items}]
      :read-option (fn [{:keys [id]} current]
                     (when (= id :topic)
                       ((:read! mini)
                         "Topic:"
                         {:initial (or current
                                       (when (and branch (not= branch g-branch)) branch)
                                       "")})))}]

    (when-let [{:keys [action switches options]} ((:transient! mini) spec)]''')

# --- mini :transient! ---
src = sub1(src, '''          :transient! (fn [title spec read-option]
                        (magit-transient! screen
                                          g
                                          left
                                          inner-w
                                          hint-row
                                          text-w
                                          title
                                          spec
                                          read-option
                                          ;; The popup opens INSIDE the status buffer's own
                                          ;; frame and may never climb over the box's top
                                          ;; border or the rows it keeps visible.
                                          {:min-row content-top}))}]''',
'''          :transient! (fn [spec]
                        (tr/run! (transient-host screen g)
                                 {:left left
                                  :inner-w inner-w
                                  :hint-row hint-row
                                  :text-w text-w
                                  ;; The popup opens INSIDE the status buffer's own
                                  ;; frame and may never climb over the box's top
                                  ;; border or the rows it keeps visible.
                                  :min-row content-top}
                                 spec))}]''')
print("ok")