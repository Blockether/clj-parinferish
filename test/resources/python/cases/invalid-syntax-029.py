> 
# Integrity cross-check of the already-recorded artifact: sum(daily_pnl) vs equity path.
for name, rows in daily["daily_rows"].items():
    tot = sum(float(r["daily_pnl_usdc"]) for r in rows)
    eq = float(rows[-1]["equity_close_usdc"]) - 100.0
    cum = float(rows[-1]["cumulative_pnl_usdc"])
    print(f"{name:26s} days={len(rows):4d} sum_daily={tot:+.10f} equity-100={eq:+.10f} cum={cum:+.10f} "
          f"| d1={abs(tot-eq):.2e} d2={abs(tot-cum):.2e}")
