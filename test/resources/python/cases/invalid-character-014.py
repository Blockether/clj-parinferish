« = None
out = await sp("eval-js " + shlex.quote("(() => { history.back(); return 'back'; })()"))
import asyncio; await asyncio.sleep(1.5)
print((await probe("(() => JSON.stringify({title: document.title, url: location.href, rows: document.querySelectorAll('[data-session-id]').length, btns: document.querySelectorAll('button').length}))()")))