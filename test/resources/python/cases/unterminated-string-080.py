menu_sh = await shell("osascript <<'APPLESCRIPT'
tell application \"System Events\"
  tell process \"Safari\"
    set frontmost to true
    set names to name of every menu bar item of menu bar 1
    return names
  end tell
end tell
APPLESCRIPT")
menu_res = await menu_sh.wait(10)
print(menu_res.get("out", ""))