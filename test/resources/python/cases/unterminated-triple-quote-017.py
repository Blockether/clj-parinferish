res=await patch(root/'test/com/blockether/vis/internal/prompt_test.clj',[{"from":"212:6ea","to":"214:513","replace":"""                        ;; Svar owns prompt-cache policy; the core tells the model which explicit
                        ;; provider-cache fields it receives and separates transport continuation.
                        \"`prompt_cache.token_read_percent`\" \"`request_hit_percent`\"
                        \"WebSocket delta continuation is separate transport telemetry\"""}]); print(res)