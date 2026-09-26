import pathlib
root = pathlib.Path('/home/user/CryptoSyf')
p = root/'tests/test_doji_study.py'
s = p.read_text()

# 1) tail must be a rising ramp so daily lows stay strictly above the trailing quick stop
old = """    for offset in range(1, tail_days + 1):
        bars.append(rising_day(trade_day + timedelta(days=offset), tail_close))"""
new = """    for offset in range(1, tail_days + 1):
        bars.append(rising_day(trade_day + timedelta(days=offset), tail_close + 0.1 * offset))"""
assert old in s
s = s.replace(old, new)

# 2) stale test mixed raw bars with daily aggregates
old = "    stale += doji_study.daily_bars(doji_series(TRADE_DAY)[24 * 22 :])"
assert old in s
s = s.replace(old, "    stale += doji_series(TRADE_DAY)[24 * 22 :]")

# 3) expected closes now ride the ramp
old = "    assert trade[\"exit_reference_price\"] == pytest.approx(141.3)"
assert old in s
s = s.replace(old, "    assert trade[\"exit_reference_price\"] == pytest.approx(141.3 + 0.1 * 19)")

# end_of_window exits on the last tail day (offset 6)
old2 = "    assert trade[\"exit_reference_price\"] == pytest.approx(141.3)\n    \n" if old2 := None else None
