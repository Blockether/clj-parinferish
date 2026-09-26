a1 = attach(str(tmp/"timeout-before.png"), filename="tui-timeout-before.png",
            label="PRZED: karta ⧖ timed out powtarza FORM + STDOUT + TIMEOUT")
a2 = attach(str(tmp/"timeout-after.png"), filename="tui-timeout-after.png",
            labels := None or "PO: linia bledu Timeout (300s) + zwykly RESULT ze stdout")
print(a1, a2)