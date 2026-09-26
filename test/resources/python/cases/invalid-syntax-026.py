reg3matrix = r'''(defdescribe
  cached-registration-helper-reload-test
  ;; Issue #176: characterize imported registration and call-time initialization.
  ;; The reported duplicate registration has not been reproduced with this fixture.
  (it "keeps namespace discovery and repeated calls working across sessions and reload"
    (with-fresh-loaded
      {"entry.py" "from registration_helper import register\nregister()\n"
       "other.py" "import blockether.vis.extension as vis\nvis.register(vis.Extension(name='other-registration', description='Independent registration'))\n"
       "registration_helper/__init__.py"
       "import blockether.vis.extension as vis\nclass Probe:\n    def ready(self):\n        '''Return the registration owner.'''\n        return vis._registration['spec']['name']\ndef register():\n    vis.register(vis.Extension(name='helper-reload', alias='helper_reload', description='Reload fixture', symbols=[vis.Symbol(Probe(), name='probe')]))\n"}
      (fn [result {:keys [ext-dir]}]
        (expect (= 2 (:loaded result)) (pr-str (pyx/load-failures)))
        (letfn [(with-session [f]
                  (let [made (ep/create-python-context {}
                               (constantly [(.getCanonicalPath ^java.io.File ext-dir)])
                               {:worker? true :jail-enabled? true :enabled? false
                                :allowed-domains [] :denied-domains [] :exclude-domains []}
                               nil)
                        ctx (:python-context made)]
                    (try (f {:python-context ctx :extensions (atom [])
                             :active-extensions (atom [])})
                         (finally (ep/dispose-python-context! ctx)))))
                (check-session [env]
                  (let [ext (registered "helper-reload")]
                    (lp/sync-active-extension-symbols! env [ext])
                    (let [out (ep/run-python-block
                                (:python-context env)
                                "assert 'Return the registration owner' in doc('probe.ready')\nfor _ in range(3):\n    assert await probe.ready() == 'helper-reload'\nprint('ready')")]
                      (expect (nil? (:error out)) (pr-str out))
                      (expect (= "ready" (str/trim (:stdout out))))))]
          (with-session
            (fn [first-env]
              (with-session
                (fn [second-env]
                  (doseq [_ (range 2)]
                    (doseq [env [first-env second-env]] (check-session env))
                    (let [reloaded (pyx/reload-python-extensions! {:dirs [(str ext-dir)]})]
                      (expect (= 0 (:failed reloaded)) (pr-str (pyx/load-failures)))
                      (expect (= 2 (:loaded reloaded)))))
                  (doseq [env [first-env second-env]] (check-session env)))))))))))
'''
print(patch(test3path,[{'from':'181:ca8','to':'202:ba6','replace':reg3matrix}]))
print(run_tests({'language':'clojure','ns':'com.blockether.vis.internal.python.extensions-test/cached-registration-helper-reload-test'}))