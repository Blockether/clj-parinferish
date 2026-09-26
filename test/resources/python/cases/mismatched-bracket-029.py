scroll_clj = tui_src / "com/blockether/vis/ext/channel_tui/scroll.clj"
input_clj = tui_src / "com/blockether/vis/ext/channel_tui/input.clj"
input_test_dir = tui_test / "com/blockether/vis/ext/channel_tui"
scroll_reads, protocol_helper_hits, terminal_lifecycle_hits = await gather(
    gather(cat(str(scroll_clj), 1, 420), cat(str(input_clj), 1, 120)),
    grep({"query": ["bare-escape?", "ctrl-abort-key?", "normalize-abort-key", "ISOControl", "raw BEL", "raw ESC", "KeyType/Character"], "paths": [str(tui_src), str(input_test_dir)], "context": 3}),
    grep({"query": ["MouseCaptureMode", "setMouseCaptureMode", "enable-terminal-state!", "disable-terminal-state!", "2004", "1006", "DECSET", "DECRST", "\\u001b[?"], "stty"], "paths": [str(tui_src), str(input_test_dir)], "context": 3})
)
print("SCROLL+INPUT READS\n", "\n".join(str(x) for x in scroll_reads))
print("\nPROTOCOL HELPERS\n", protocol_helper_hits)
print("\nLIFECYCLE\n", terminal_lifecycle_hits)