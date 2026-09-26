root = Path(session["workspace"]["root"])
path = root / "resources/examples/python-extensions/remote_sandboxed_server.py"
src = path.read_text()
fixed = src.replace('" \\"$(cut -d\' \' -f1 /proc/uptime)\\""', ' \'$(cut -d" " -f1 /proc/uptime)\'')
fixed = fixed.replace(' "\\"$(awk \\'/^MemTotal/{print $2}\\' /proc/meminfo)\\""', " \'$(awk \\'/^MemTotal/{print $2}\\' /proc/meminfo)\'")
