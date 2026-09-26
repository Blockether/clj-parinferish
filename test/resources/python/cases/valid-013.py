import httpx as hx
queries=[
 'WKWebView fetch blob URL hangs second fetch resolves',
 'iOS WKWebView fetch blob URL pending until user interaction',
 'Safari fetch blob url hangs share click',
 'Capacitor fetch blob URL hangs iOS',
]
async def search_web(q):
    url='https://www.google.com/search?q='+__import__('urllib.parse').parse.quote(q)
    async with hx.AsyncClient(timeout=15,headers={'User-Agent':'Mozilla/5.0'}) as c:
        r=await c.get(url)
    return q,r.status_code,re.sub(r'<[^>]+>',' ',r.text)[:5000]
results=await gather(*(search_web(q) for q in queries))
for q,status,text_body in results:
    snippets=[re.sub(r'\s+',' ',x).strip() for x in text_body.split('\n') if any(k in x.lower() for k in ('wkwebview','blob','capacitor','safari'))]
    print('\nQUERY',q,'STATUS',status,'\n', '\n'.join(snippets[:12])[:3000])