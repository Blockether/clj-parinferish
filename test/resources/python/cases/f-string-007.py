UDID="B533BA6A-09C3-43C3-9821-7E2BD0792A95"
r = await shell(op="run", commands=[
  f"xcrun simctl spawn {UDID} defaults write com.apple.Accessibility ReduceMotionEnabled -int 1 2>&1|tail -2; xcrun simctl terminate {UDID} com.blockether.viscompanion >/dev/null 2>&1; sleep 1; xcrun simctl launch {UDID} com.blockether.viscompanion 2>&1|tail -1; sleep 6; pgrep -lf 'WebContentExtension' | awk '{print $1}'",
], timeout_secs=300)
print(r["commands"][0]["stdout"])