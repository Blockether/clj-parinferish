iomenu = await shell("osascript <<'APPLESCRIPT'\ntell application \"System Events\"\n tell process \"Simulator\"\n  set rows to {}\n  tell menu 1 of menu bar item \"I/O\" of menu bar 1\n   repeat with mi in menu items\n    set n to name of mi
    set m to missing value
    try
      set m to value of attribute \"AXMenuItemMarkChar\" of mi
    end try
    set end of rows to n & \"|\" & (m as text)
   end repeat
  end tell
  return rows
 end tell
end tell\nAPPLESCRIPT")
io_out = await iomenu.wait(10)
print(io_out.get("out", ""))