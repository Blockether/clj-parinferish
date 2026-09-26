s=open(P).read()
pairs=[
("""(defn shell-logs
  "`await shell_logs(\\"dev\\")` — read a background shell's log from a byte offset""",
 """(defn shell-logs
  "`sh.logs()` — read a background shell's log from a byte offset"""),
("""(defn shell-type
  "`await shell_type(\\"dev\\", \\"y\\")` — type keystrokes at a background shell's stdin.
   `is_enter` (default true) submits the line, which is what an interactive prompt
   waits for; read the response with `shell_logs`.\"""",
 """(defn shell-type
  "`sh.type(\\"y\\")` — type keystrokes at a background shell's stdin.
   `is_enter` (default true) submits the line, which is what an interactive prompt
   waits for; read the response with `sh.logs()`.\""""),
("""(defn shell-stop
  "`await shell_stop(\\"dev\\")` — kill the process tree""",
 """(defn shell-stop
  "`sh.stop()` — kill the process tree"""),
('     :name "shell_logs"', '     :name "_shell_logs"'),
('     :name "shell_type"', '     :name "_shell_type"'),
('     :name "shell_stop"', '     :name "_shell_stop"'),
("""  "`await shell_logs(\\"dev\\")` — read a background shell's log from a byte offset
   and return NOW; nothing blocks on your behalf — a wait is a bounded loop you
   write in `python_execution` and break on what you read. No offset reads the TAIL;
   `offset=0` starts at the beginning. Live ids: `session[\\"resources\\"]`.\"""",
 """  "TRANSPORT for `sh.logs(offset=…, limit=…)`; call the HANDLE, not this. Reads a
   background shell's log from a byte offset and returns NOW. No offset reads the
   TAIL; `offset=0` starts at the beginning. Live ids: `session[\\"resources\\"]`.\""""),
("""     "Type keystrokes at a background shell's stdin; `is_enter` (default true) submits the line."''",
 ""),
]
pairs=[p for p in pairs if p[1] or True]
