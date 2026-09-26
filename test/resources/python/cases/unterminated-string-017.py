patch(project_root_path/'src/com/blockether/vis/internal/decisions/cache.clj',[{'from':'75:0b3','to':'81:942','replace':'      (let [idle (sort-by (comp :used second)
                          (for [[k v] @entries
                                :when (and (= :ready (:status v)) (zero? (:users v)))]
                            [k v]))'},{'from':'127:565','to':'144:543','replace':'    (if-let [loaded (:load selection)]
      (try (doseq [entry (:evicted selection)]
             (close! entry))
           (let [value (loader)]
             (locking lock
               (swap! entries assoc
                 key
                 (-> (get @entries key)
                     (assoc :status :ready :value value)))
               (deliver loaded {:ok true}))
             (try (operation value) (finally (release! key))))
           (catch Throwable e
             (locking lock
               (when (= :loading (:status (get @entries key)))
                 (swap! entries dissoc key)
                 (deliver loaded {:error e})))
             (throw e)))'},{'from':'163:944','replace':'                                          (and (= :ready (:status entry)) (zero? (long (:users entry)))))'}]); print('cache patched')