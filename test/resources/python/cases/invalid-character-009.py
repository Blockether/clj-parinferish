« # session_fold real call sites
sf = []
for x in I:
    for ln in x["code"].splitlines():
        st = ln.strip()
        if re.match(r"^\s*(?:[\w ,=]+=\s*)?(?:await\s+)?session_fold\s*\(", ln) or st.startswith("session_fold("):
            sf.append((x["sid"], x["turn"], x["pos"], st[:150]))
print("session_fold invocation lines:", len(sf))
for r_ in sf[:20]: print(f'{r_[0]} t{r_[1]}/i{r_[2]} {r_[3]}')
»
