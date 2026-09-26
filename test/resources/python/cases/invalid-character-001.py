sp = Path("/home/user/CryptoSyf/research/sources.json")
raw = sp.read_text()
src = json.loads(raw)
assert json.dumps(src, ensure_ascii=False, indent=2) + "\n" == raw, "format differs"
for api in src["apis"]:
    if api["host"] in ("api.dexscreener.com", "lite-api.jup.ag") and "public-meme" not in api["used_by"]:
        api["used_by"].append("public-meme")
hosts = {a["host"] for a in src["apis"]}
new_apis = [
    {"host": "api.gopluslabs.io", "role": "fakty kontraktu tokenów Solana (token_security w partiach do 30 mintów), odczyt po t0", "in_ledger": True, "used_by": ["public-meme"], "cost": "publiczny GET, 0 kredytów"},
    {"host": "api.rugcheck.xyz", "role": "niezależne podsumowanie ryzyka tokenu (report/summary per mint) do krzyżowej kontroli GoPlus", "in_ledger": True, "used_by": ["public-meme"], "cost": "publiczny GET, 0 kredytów"},
]
for a in new_apis:
    if a["host"] not in hosts:
        src["apis"].append(a)
abstracts = [
    ("2607.02823v3", "pump.fun: 832 941 launchów, tylko 0,198 % „graduates" — bazowa stopa porażki, nie parametr."),
    ("2601.22185v1", "MemeChain: 5,15 % tokenów żyje dłużej niż 24 h — kontekst progów przeżycia t1/t7d/t30d."),
    ("2507.01963v2", "Midsummer: 82,8 % badanych meme tokenów kończy jako pułapka lub upadek płynności."),
    ("2602.13480v2", "MELT: 36,5 % podaży w rękach koordynowanych klastrów — uzasadnienie ostrzeżenia top-10."),
    ("2607.02795v3", "Kohorty sniperów: lift +16,1 % w wczesnym przewidywaniu; metoda, nie sygnał."),
    ("2608.20271v1", "Wczesne wykrywanie oszukańczych memecoinów z cech on-chain — definicje cech, nie model."),
    ("2603.24625v2", "Dynamika płynności i wycofań na launchpadach Solana — kontekst LIQUIDITY_COLLAPSED."),
    ("2609.10246v1", "Struktura rynku meme tokenów na Solanie — opis, bez reguły wejścia."),
    ("2602.14860v1", "Manipulacja i koncentracja posiadaczy — motywacja dla flag koncentracji i LP."),
    ("2504.07132v1", "SolRPDS: zbiór danych rug-pulli Solana — etykiety referencyjne, nie użyte do treningu."),
    ("2512.00377v2", "ME2F: wielomodalne cechy meme tokenów — definicje, bez odtworzenia wyników."),
    ("1902.06976v2", "Honeypoty EVM (87 % wykrywalności) — wyłącznie definicja operacyjna honeypota."),
]
doc_ids = {d["id"] for d in src["docs"]}
for arx, taken in abstracts:
    did = f"arxiv-{arx}"
    if did in doc_ids:
        continue
    src["docs"].append({
        "id": did,
        "url": f"https://arxiv.org/abs/{arx}",
        "read_utc": "2026-09-11",
        "archive": None,
        "taken": taken,
        "used_by": ["public-meme"],
        "state": "ABSTRACT_ONLY_NOT_ARCHIVED",
    })
sp.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n")
print(len(src["apis"]), len(src["docs"]))

ap = Path("/home/user/CryptoSyf/AGENTS.md")
a = ap.read_text()
anchor = " - Publiczny cap żądań został podniesiony z 40 do 222 zapisaną zgodą\n"
assert a.count(anchor) == 1
i = a.index(anchor)
# find end of that bullet (next line starting with '- ' or ' - ' or blank)
j = a.index("\n\n", i)
bullet = """
 - `public-meme` (MEME-RISK-v1, t55) to diagnostyka ryzyka meme tokenów na zamrożonej
   kohorcie DEX-MULTISOURCE100-v1: przeżycie płynności t1/t7d/t30d (DexScreener),
   fakty kontraktu po t0 (GoPlus, RugCheck), drabinka głębokości Jupiter 10/100/1000 USDC
   i tabela progu brutto po kosztach i podatku (UNVERIFIED_LAW). Zawsze INCONCLUSIVE:
   brak reguły wejścia, brak zwrotów, przeżycie per flaga jest opisowe (MDE 25–50 pp).
   Werdykty PAPER_WATCHLIST/EXCLUDED/INCONCLUSIVE nie są listą zakupów; brak odczytu
   nigdy nie jest „bezpieczny". Cap żądań publicznych podniesiony 384→480 zapisaną
   zgodą w t55 (zadanie użytkownika, 0 kredytów); odczyty t7d/t30d otwierają się
   2026-09-16T17:34:32Z i 2026-10-09T17:34:32Z — nie odświeżać wcześniej."""
a = a[:j] + bullet + a[j:]
ap.write_text(a)
print(a[i:j+len(bullet)+2][-700:])