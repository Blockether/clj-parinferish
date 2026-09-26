r=patch(p,[{'from':'1094:6fe','to':'1098:623','replace':'''                      row-left (+ left
                                  (if child? 1 0)
                                  (if (#{:project-group :project-session} kind) 1 0)
                                  (if (:nested? entry) 1 0))
                      name-width (max 0 (- status-col row-left 1))]]''},{'from':'1107:141','to':'1108:0fb','replace':'''            (p/styled g
                      (if (or (#{:project-select :project-set} kind) active? focused?) [p/BOLD] [])'''},{'from':'1122:cd1','to':'1123:ed6','replace':'''                                                        :project-group
                                                        (if (:folded? entry) "▸ " "▾ ")'''}]); print(r)