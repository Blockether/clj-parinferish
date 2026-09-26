chrome_profile = Path.home() / ".vis" / "chrome-cdp-profile"
chrome_profile.mkdir(parents=True, exist_ok=True)
chrome_port = 9223
launch_cmd = (
    "/usr/bin/open -na 'Google Chrome' --args "
    f"--remote-debugging-address=127.0.0.1 --remote-debugging-port={chrome_port} "
    f"--remote-allow-origins='*' --user-data-dir={shlex.quote(str(chrome_profile))} "
    "--no-first-run --no-default-browser-check about:blank; "
    f"for i in $(seq 1 30); do lsof -nP -iTCP:{chrome_port} -sTCP:LISTEN 2>/dev/null && exit 0; sleep 0.5; done; exit 1"
launch = await shell(launch_cmd, cwd=str(root))
launch_state = await launch.wait(20)
print({"status": launch_state.get("status"), "exit": launch_state.get("exit"), "port": chrome_port, "profile": str(chrome_profile)})
print(launch.logs(-20))