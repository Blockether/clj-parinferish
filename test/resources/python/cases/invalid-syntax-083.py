import subprocess, pathlib
css = pathlib.Path("/home/user/vis/extensions/channels/vis-channel-web/resources/vis-channel-web/public/app.css").read_text()

def icon(): return '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/></svg>'

def chip(label, in$, out$, cur=False):
    price = f'<span class="mc-price" title="in/out">{in$}<span class="mc-price-sep">/</span>{out$}</span>' if in$ else ''
    return (f'<button type="button" class="model-chip{" current" if cur else ""}">'
            f'<span class="mc-icon">{icon()}</span><span class="mc-name">{label}</span>{price}</button>')

groups = [("ANTHROPIC (CLAUDE SUBSCRIPTION)", [("claude-opus-4-8","$5","$25"),("claude-fable-5","$10","$50"),
          ("claude-opus-4-7","$5","$25"),("claude-opus-4-6","$5","$25"),("claude-sonnet-4-6","$3","$15"),("claude-haiku-4-5","$1","$5")]),
          ("OPENAI CODEX (CHATGPT OAUTH)", [("gpt-5.6-sol","$5","$30"),("gpt-5.6-terra","$2.5","$15"),("gpt-5.5","$5","$30"),("gpt-5.4","$2.5","$15"),("gpt-5.3-codex","$1.75","$14")])]

body = ['<div id="model-pick">',
        '<p class="active-model">This session: <strong>anthropic-coding-plan/claude-opus-4-8 (default)</strong></p>',
        '<div class="model-groups">',
        '<div class="model-chips pick">'+chip("router default","","",cur=True)+'</div>']
for name, models in groups:
    body.append(f'<div class="model-group"><p class="model-group-label">{name}</p><div class="model-chips pick">')
    body += [chip(n,i,o) for n,i,o in models]
    body.append('</div></div>')
body.append('</div></div>')
inner = "".join(body)

measure = """
<pre id="M"></pre><script>
function r(el){const b=el.getBoundingClientRect();return [Math.round(b.left),Math.round(b.right),Math.round(b.width)];}
window.addEventListener('load',()=>{
  const out=[];
  const chip=document.querySelectorAll('.model-group .model-chip')[0];
  out.push('CHIP    '+r(chip));
  out.push('ICON    '+r(chip.querySelector('.mc-icon')));
  out.push('NAME    '+r(chip.querySelector('.mc-name')));
  out.push('PRICE   '+r(chip.querySelector('.mc-price')));
  const chips=document.querySelectorAll('.model-group')[0].querySelectorAll('.model-chip');
  out.push('rowchips widths '+[...chips].map(c=>Math.round(c.getBoundingClientRect().width)));
  const cont=document.querySelector('.model-group .model-chips');
  out.push('CONTAINER '+r(cont));
  document.getElementById('M').textContent=out.join('\\n');
});
</script>"""

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}
body{{margin:0}} .overlay{{display:block}} .modal{{}}</style></head>
<body><div class="overlay"><div class="modal settings-modal" style="display:block"><div class="modal-head"><h2>Session model</h2></div>
<div class="modal-body">{inner}</div></div></div>{measure}</body></html>"""
pathlib.Path("/tmp/repro.html").write_text(html)

# render at phone width via headless chrome, dump DOM (after JS)
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
res=subprocess.run([chrome,"--headless=new","--disable-gpu","--window-size=402,900",
    "--virtual-time-budget=1500","--dump-dom","file:///tmp/repro.html"],capture_output=True,text=True,timeout=60)
import re
m=re.search(r'<pre id="M">(.*?)</pre>', res.stdout, re.S)
print(m.group(1) if m else res.stdout[-2000:])
print("stderr tail:", res.stderr[-300:])
