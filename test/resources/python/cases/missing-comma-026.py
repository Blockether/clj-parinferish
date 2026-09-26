S="vis-fleet-t7"
def sh(cmds, t=180):
    return ntr_run(cmds, t)
r = await shell(commands=[
 f"S={S}; spel --session $S storage local set 'CapacitorStorage.vis.connections' \"$(cat /tmp/vis-conns-3.json)\" >/dev/null && spel --session $S storage local set 'vis.connections' \"$(cat /tmp/vis-conns-3.json)\" >/dev/null && spel --session $S open --viewport 390x844 'http://localhost:5273' >/dev/null && sleep 4 && spel --session $S eval-js \"(() => {const i=document.querySelector('input[aria-label=\\\"Filter sessions\\\"]'); const set=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set; set.call(i,'graalvm'); i.dispatchEvent(new Event('input',{bubbles:true})); return 'typed';})()\" && sleep 3 && spel --session $S eval-js \"(() => JSON.stringify({head:document.querySelector('main').innerText.slice(0,140), regs:[...document.querySelectorAll('section')].map(s=>s.getAttribute('aria-label'))}))()\" && spel --session $S screenshot /tmp/vis-e2e/s1-fleet-search-phone.png >/dev/null && echo SHOT1"
], timeout_secs=180)
print(r["commands"][0]["stdout"][-900:], r["commands"][0]["stderr"][-400:])
