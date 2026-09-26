> 
t = t[:i] + t[j:]                                  # drop clj-repair-source
rep("(clj-repair-source code)", "(repair/repair-source code)", 2)
rep('''  ([code] (clj-repair+format code nil))
  ([code path] (fmt/format-source (:code (clj-repair-source code)) path)))''',
    '''  ([code] (clj-repair+format code nil))
  ([code path] (fmt/format-source (:code (repair/repair-source code)) path)))''', 0) if False else None
print("repair-source call sites:", t.count("(repair/repair-source code)"))
print(t[t.index("(defn clj-repair+format"):t.index("(defn- relativize-path")])