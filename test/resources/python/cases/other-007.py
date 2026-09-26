import sqlite3, json
conn = sqlite3.connect(f"file:{project_root_path}/data/nansen-pilot.sqlite?mode=ro", uri=True)
STABLES = {"USDC","USDT","DAI","FDUSD","PYUSD","USDE","USD1","SUSDE","SUSDS"}
for sid, req, body in conn.execute(
    "SELECT id, request_json, body_json FROM snapshots WHERE endpoint LIKE '%historical-token-balances%' ORDER BY id"
):
    as_of = json.loads(req)["as_of_date"]
    rows = json.loads(body)["data"]
    sol = [r for r in rows if r.get("chain") == "solana" and str(r.get("token_symbol")) not in STABLES]
    shares = sorted((r["share_of_holdings_percent"], str(r["token_symbol"])) for r in sol if isinstance(r.get("share_of_holdings_percent"), (int, float)), reverse=True)
    print(as_of, "| solana non-stable:", len(sol), "| top:", shares[:6])
conn.close()
