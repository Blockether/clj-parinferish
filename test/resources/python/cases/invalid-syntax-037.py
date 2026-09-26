tui_html = out_dir / "provider-failure-tui.html"
tui_text = tui_html.read_text()
tui_soup = BeautifulSoup(tui_text, "html.parser")ntui_linked = [(tag.name, tag.get("src"), tag.get("href")) for tag in tui_soup.find_all(True) if tag.get("src") or tag.get("href")]
ignore_check = await run_shell_result("git check-ignore -v target/error-card-review", companion_root, 30)
visible_tui = " ".join(tui_soup.stripped_strings)
print(json.dumps({
    "tui": {"path": str(tui_html), "bytes": tui_html.stat().st_size, "linked": tui_linked, "has_what_happened": "WHAT HAPPENED" in visible_tui.upper(), "has_next_step": "NEXT STEP" in visible_tui.upper()},
    "temp_build_ignore": brief_shell(ignore_check),
}, indent=2))