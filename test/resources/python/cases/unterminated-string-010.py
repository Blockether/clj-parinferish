print(patch(project_root_path/'src/com/blockether/vis/internal/activity/core.clj',[{'from':'221:491','to':'222:539','replace':'        state
        (if (= kind :shell) (:state (last children)) (grouped-state children))

        shell-view
        (when (= kind :shell) (presenter/shell-receipt-presentation children))'},{'from':'240:770','replace':'              :summary (cond (= kind :shell) (or (get shell-view "summary") (:summary first-row))'},{'from':'247:e6a','to':'248:aa8','replace':'       shell-view
       (assoc :presentation shell-view)

       (and (= kind :shell) (= :failed state) (:error-summary (last children)))
       (assoc :error-summary (:error-summary (last children)))

       (and (= kind :shell) (= :shell (:operation first-row)) (:argument-key first-row))
       (assoc :argument-key (:argument-key first-row))'},{'from':'259:438','to':'285:3dd','replace':'(defn- coalesce-shell-rows
  [rows]
  (let [key-for #(when (= :shell (:presenter %)) (resource-key-of-type % :shell-handle))
        by-handle (reduce (fn [groups row]
                            (if-let [key (key-for row)]
                              (update groups key (fnil conj []) row)
                              groups))
                          {}
                          rows)]
    (loop [remaining rows emitted #{} result []]
      (if-let [row (first remaining)]
        (let [key (key-for row)]
          (cond (and key (contains? emitted key))
                (recur (rest remaining) emitted result)
                (and key (next (get by-handle key)))
                (recur (rest remaining)
                       (conj emitted key)
                       (conj result (grouped-row :shell (get by-handle key))))
                :else (recur (rest remaining) emitted (conj result row))))
        result))))'}]))