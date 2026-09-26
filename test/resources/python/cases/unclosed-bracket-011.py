from datetime import UTC, date, datetime, timedelta

def day_bars(day, open_, close, high=None, low=None, volume=10.0):
    high = max(open_, close) if high is None else max(open_, close, high)
    low = min(open_, close) if low is None else min(open_, close, low)
    first = Candle(datetime(day.year, day.month, day.day, tzinfo=UTC), open_, high, low, close, volume, volume * close)
    rest = [Candle(datetime(day.year, day.month, day.day, h, tzinfo=UTC), close, close, close, close, volume, volume * close) for h in range(1, 24)]
    return [first, *rest]

def flat_days(start, count, price=100.0):
    return [day_bars(start + timedelta(days=o), price, price, price + 0.3, price - 0.3) for o in range(count)]

def down_leg(start, count, first_price, step=2.0):
    out, p = [], first_price
    for o in range(count):
        out.append(day_bars(start + timedelta(days=o), p, p - step, p + 0.5, p - step - 0.5)); p -= step
    return out

def up_leg(start, count, first_price, step=1.0):
    out, p = [], first_price
    for o in range(count):
        out.append(day_bars(start + timedelta(days=o), p, p + step, p + step + 0.5, p - 0.5)); p += step
    return out

def sar_series(tail="win"):
    days = day_bars(date(2024, 12, 16), 100.0, 100.0, 100.5, 99.5)
    days += [b for d in down_leg(date(2024, 12, 17), 20, 100.0) for b in d]
    base = 100.0 - 2 * 20  # 60
    # rally day 2025-01-06 flips the trend up
    days += day_bars(date(2025, 1, 6), base, base + 15, base + 16, base - 0.5)
    if tail == "win":
        days += [b for d in up_leg(date(2025, 1, 7), 55, base + 15) for b in d]          # rise to ~130
        days += day_bars(date(2025, 3, 3), base + 70, base + 60, base + 70.5, base + 25)  # crash, low ~85
        days += flat_days(date(2025, 3, 4), 28, base + 60)
    elif tail == "lose":
        days += day_bars(date(2025, 1, 7), base + 15, base - 12, base + 16, base - 15)    # entry-day crash
        days += flat_days(date(2025, 1, 8), 83, base - 12)
    else:  # rising
        days += [b for d in up_leg(date(2025, 1, 7), 84, base + 15) for b in d]
    return [b for d in days for b in d]

import json
cfg = json.loads(Path("/home/user/CryptoSyf/research/public-pilot.json").read_text())
CFG = next(e for e in cfg["experiments"] if e["id"] == "PARABOLIC-SAR100-v1")
start, end = datetime.fromisoformat("2025-01-01T00:00:00+00:00"), datetime.fromisoformat("2025-04-01T00:00:00+00:00")
for tail in ("win", "lose", "rising"):
    days = daily_bars(sar_series(tail))
    sigs = sar_study.sar_signals(days, start, end, CFG)
    sar, trend = sar_study._sar_series(days)
    run = sar_study.simulate_asset(days, sigs, start=start, end=end, cost_bps=0, config=CFG)
    tr = run["trades"][0] if run["trades"] else None
    print(tail, "| signals:", [(str(s['signal_date']), str(s['trade_date'])) for s in sigs],
          "| trades:", run["closed_trades"], "| pnl:", round(run["net_pnl_usdc"], 2),
          "| exit:", tr and tr["exit_reason"], tr and (str(days[[i for i,d in enumerate(days) if d['date'].isoformat()==tr['exit_at'][:10]][0]]["close"]))
