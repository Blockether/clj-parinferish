import httpx as hx
queries = [
    'site:developer.apple.com/forums AVSpeechSynthesizer "Siri Voice" speechVoices',
    'site:developer.apple.com/documentation/avfaudio AVSpeechSynthesisVoice speechVoices Siri',
    'AVSpeechSynthesisVoice Siri Voice 1 not listed third party app',
    'iOS AVSpeechSynthesizer Siri voices unavailable accessibility voices',
]
async def search_web(q):
    url = "https://html.duckduckgo.com/html/"
    async with hx.AsyncClient(follow_redirects=True, timeout=20) as client:
        resp = await client.get(url, params={"q": q}, headers={"User-Agent": "Mozilla/5.0"})
    return q, resp.status_code, resp.text[:200000]
results = await gather(*(search_web(q) for q in queries))
from bs4 import BeautifulSoup
for q, status, html in results:
    soup = BeautifulSoup(html, "html.parser")
    rows=[]
    for result in soup.select(".result")[:8]:
        a=result.select_one(".result__a")
        snippet=result.select_one(".result__snippet")
        if a: rows.append((a.get_text(" ", strip=True), a.get("href"), snippet.get_text(" ", strip=True) if snippet else ""))
    print("\nQUERY", q, "status", status)
    for title, href, snippet in rows:
        print("-", title, "|", href, "|", snippet[:300])