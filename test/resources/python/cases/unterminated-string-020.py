print(patch(project_root_path/'test/com/blockether/vis/internal/docs/core_test.clj',[{'from':'638:cfa','to':'644:ad3','replace':'    "keeps mobile and published-release desktop buttons readable without the documentation stylesheet"
    (let [published
          (second (re-find #"class=\\"store-windows\\" href=\\"https://github.com/Blockether/vis/releases/download/v([0-9]+\\.[0-9]+\\.[0-9]+)/"
                           (slurp "README.md")))

          release
          (str "https://github.com/Blockether/vis/releases/download/v" published
               "/vis-companion-" published)]

      ;; VIS_VERSION can advance before a release exists. Both guides keep the last
      ;; published download until the new artifacts are available.
      (expect (some? published))'}]))