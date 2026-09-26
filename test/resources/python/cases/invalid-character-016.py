« # check B8B8B8 on light
cnt=Counter()
for s in secs[1:]:
    rects=[]
    for m in re.finditer(r'<div class="r"[^>]*style="([^"]+)"',s):
        st=m.group(1); bg=re.search(r'background:(#[0-9A-Fa-f]{6})',st)
        if bg and bg.group(1).upper() in dark_bgs:
            l,tp,w,h=num(st,'left'),num(st,'top'),num(st,'width'),num(st,'height')
            if None not in (l,tp,w,h) and w>100 and h>40: rects.append((l,tp,w,h))
    for m in re.finditer(r'<div class="t[^"]*"[^>]*style="([^"]+)"',s):
        st=m.group(1); l,tp=num(st,'left'),num(st,'top')
        if "#B8B8B8" in st.upper():
            on=any(rl<=l<=rl+rw and rt<=tp<=rt+rh for rl,rt,rw,rh in rects)
            cnt[on]+=1
print(cnt) »