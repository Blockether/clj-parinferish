print(await patch(pf,[
 {'from':'680:d67','to':'683:b3b','replace':'        ;; The contract is the wall, not its production length. A promise keeps the\n        ;; callback provably wedged, so 100ms exercises the same timeout without\n        ;; adding two seconds to every suite run.'},
 {'from':'685:c15','replace':'          (with-redefs [providers/probe-timeout-ms 100]'},
 {'from':'717:515','to':'720:a32','replace':'  (let [;; The contract is the wall, not its production length. The stand-in\n        ;; outlives the test ceiling fivefold without parking the suite for seconds.'},
 {'from':'722:249','replace':'        (with-redefs [providers/limits-probe-timeout-ms 100'},
 {'from':'725:de6','replace':'                        (Thread/sleep 500)'},
 {'from':'735:549','replace':'    (is (< (long (:elapsed-ms outcome)) 1000))))'
]))