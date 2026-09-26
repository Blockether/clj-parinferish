browser_session = f"agent-{int(time.time())}"
phone_light = preview_root / "filled-close-phone-light.png"
phone_dark = preview_root / "filled-close-phone-dark.png"
desktop_light = preview_root / "filled-close-desktop-light.png"
phone_scaled = preview_root / "filled-close-phone-light-130.png"
face_selector = 'button[aria-label="Close chart.png"] span'
style_js = "(() => { const e=document.querySelector('button[aria-label=\\\"Close chart.png\\\"] span'); const h=document.querySelector('[role=dialog] header'); const s=getComputedStyle(e); const hs=getComputedStyle(h); return JSON.stringify({face:{background:s.backgroundColor,color:s.color,border:s.borderColor,radius:s.borderRadius},header:{background:hs.backgroundColor,color:hs.color}}) })()"
commands = [
    f"spel --session {shlex.quote(browser_session)} set viewport 393 852",
    f"spel --session {shlex.quote(browser_session)} --content-boundaries open http://127.0.0.1:{preview_port}/",
    f"spel --session {shlex.quote(browser_session)} --content-boundaries wait --load domcontentloaded",
    f"spel --session {shlex.quote(browser_session)} get box {shlex.quote(face_selector)}",
    f"spel --session {shlex.quote(browser_session)} eval-js {shlex.quote(style_js)}",
    f"spel --session {shlex.quote(browser_session)} screenshot {shlex.quote(str(phone_light))}",
    f"spel --session {shlex.quote(browser_session)} eval-js {shlex.quote(\"document.documentElement.dataset.theme='blockether-dark'\")}",
    f"spel --session {shlex.quote(browser_session)} eval-js {shlex.quote(style_js)}",
    f"spel --session {shlex.quote(browser_session)} screenshot {shlex.quote(str(phone_dark))}",
    f"spel --session {shlex.quote(browser_session)} eval-js {shlex.quote(\"document.documentElement.dataset.theme='blockether-light';document.documentElement.style.fontSize='100%'\")}",
    f"spel --session {shlex.quote(browser_session)} set viewport 1280 800",
    f"spel --session {shlex.quote(browser_session)} get box {shlex.quote(face_selector)}",
    f"spel --session {shlex.quote(browser_session)} screenshot {shlex.quote(str(desktop_light))}",
    f"spel --session {shlex.quote(browser_session)} set viewport 393 852",
    f"spel --session {shlex.quote(browser_session)} eval-js {shlex.quote(\"document.documentElement.style.fontSize='130%'\")}",
    f"spel --session {shlex.quote(browser_session)} get box {shlex.quote(face_selector)}",
    f"spel --session {shlex.quote(browser_session)} screenshot {shlex.quote(str(phone_scaled))}",
]
render_h = await shell(" && ".join(commands), cwd=str(root))
render_result = await render_h.wait(120)
print(render_h.logs(-200))