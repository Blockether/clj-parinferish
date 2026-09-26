path='/home/user/spel/test/com/blockether/spel/ios_test.clj'; text='''

;; Regression, issue #134: Appium inherited the launcher's process group and
;; died on SIGHUP after a timed-out CLI exited, while the daemon stayed alive.
(defdescribe appium-process-lifetime-test
  "The owned Appium server outlives whichever CLI invocation started it."

  (it "ignores launcher hangup before executing Appium"
    (expect (= ["nohup" "appium" "server"
                "--address" "127.0.0.1"
                "--port" "4901"]
              (#'sut/appium-command 4901)))))
'''; with open(path,'a') as f: f.write(text)
sh=await shell('clojure -M:test --var com.blockether.spel.ios-test/appium-process-lifetime-test --var com.blockether.spel.daemon-test/ios-health-test',cwd='/home/user/spel',timeout=300); r=await sh.wait(300); print(r['out'][-3000:]); print('exit',r['exit'])