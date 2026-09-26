 integ = '''"""Cache-only public-fvg wiring on synthetic archives; no market observations."""

import copy
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from cryptosyf import public_pilot
from cryptosyf.candles import Candle, archive_url
from cryptosyf.public_data import PublicReader

PROJECT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((PROJECT / "research/public-pilot.json").read_text())
HOUR = timedelta(hours=1)
SYMBOLS = ["ADAUSDC", "AVAXUSDC", "BNBUSDC", "BTCUSDC", "DOGEUSDC", "ETHUSDC", "SOLUSDC", "XRPUSDC"]
MONTHS = ["2024-12", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10"]


def month_hours(month):
    start = datetime.fromisoformat(month + "-01T00:00:00+00:00")
    if start.month == 12:
        end = datetime(start.year + 1, 1, 1, tzinfo=UTC)
    else:
        end = datetime(start.year, start.month + 1, 1, tzinfo=UTC)
    return start, int((end - start) / HOUR)


def synthetic_month(month, symbol):
    rng = random.Random(f"{symbol}-{month}")
    start, hours = month_hours(month)
    at, price, bars = start, 100.0, []
    for _ in range(hours):
        close = price * (1 + rng.uniform(-0.006, 0.006))
        high = max(price, close) * (1 + rng.uniform(0, 0.002))
        low = min(price, close) * (1 - rng.uniform(0, 0.002))
        bars.append(Candle(at, price, high, low, close, 10.0, 10.0 * close))
        price, at = close, at + HOUR
    return bars


@pytest.mark.parametrize("collect", [False, True])
def test_cache_miss_never_sends_request_even_with_collect(tmp_path, collect):
    def forbidden(url):
        pytest.fail("Network transport must not run")

    with PublicReader(tmp_path / "p.sqlite", allow_network=collect, transport=forbidden) as reader:
        result = public_pilot.fvg_screen(reader, REGISTRY)
        assert reader.audit()["attempts"] == 0
    assert result["status"] == "BLOCKED_DATA"
    assert result["audit_complete"] and not result["collection_complete"]
    assert result["summary"] == [] and result["pooled"] == {}
    assert result["total_net_pnl_state"] == "NOT_REPORTABLE"
    assert result["information_cost"]["new_public_requests"] == 0


@pytest.mark.parametrize(
    "change",
    [
        {"archive_months": MONTHS[:-1]},
        {"symbols": SYMBOLS[:-1]},
        {"max_new_public_requests": 1},
    ],
)
def test_registration_cannot_expand_cache_scope(tmp_path, change):
    registry = copy.deepcopy(REGISTRY)
    public_pilot.active_experiment(registry, "public-fvg").update(change)
    with PublicReader(tmp_path / "p.sqlite") as reader:
        result = public_pilot.fvg_screen(reader, registry)
        assert reader.audit()["attempts"] == 0
    assert result["failure"] == "FVG_CACHE_SCOPE_CHANGED"


def cache_month(reader, month, symbol):
    url = archive_url(month, symbol)
    reader.get(url)
    reader.get(url + ".CHECKSUM")


def test_bad_checksum_keeps_full_blocked_audit_and_never_refetches(tmp_path):
    with PublicReader(
        tmp_path / "p.sqlite",
        allow_network=True,
        min_interval=0,
        transport=lambda url: b"bad synthetic archive",
    ) as reader:
        cache_month(reader, "2025-01", "SOLUSDC")
        result = public_pilot.fvg_screen(reader, REGISTRY)
        again = public_pilot.fvg_screen(reader, REGISTRY)
        assert reader.audit()["attempts"] == 2
    assert result["failure"] == "ARCHIVE_CHECKSUM_MISMATCH"
    assert result == again
    assert result["archive_audit"]["verified_assets"] == {}


def test_synthetic_cache_completes_and_replays_identically(tmp_path, monkeypatch):
    monkeypatch.setattr(
        public_pilot,
        "parse_month",
        lambda raw, checksum, *, month, symbol: synthetic_month(month, symbol),
    )
    registry = copy.deepcopy(REGISTRY)
    public_pilot.active_experiment(registry, "public-fvg")["bootstrap"]["resamples"] = 1000
    with PublicReader(
        tmp_path / "p.sqlite",
        allow_network=True,
        min_interval=0,
        transport=lambda url: b"synthetic",
    ) as reader:
        result = public_pilot.fvg_screen(reader, registry)
        replay = public_pilot.fvg_screen(reader, registry)
    assert result["collection_complete"] is True
    assert result == replay
    audit = result["archive_audit"]
    assert audit["verified_assets"] == {symbol: 11 for symbol in SYMBOLS}
    assert all(count == 11 * 744 - 3 * 24 for count in audit["verified_bars"].values())
    assert len(result["provenance"]) == 8 * 11 * 2
    assert result["information_cost"]["new_public_requests"] == 8 * 11 * 2
    assert len(result["summary"]) == 3 * 8
    assert {item["scenario"] for item in result["summary"]} == {"gross", "primary", "stress"}
    assert result["decision_reasons"]
    assert result["status"] in {"REJECTED", "INCONCLUSIVE"}
    assert set(result["daily_rows"]) == {
        f"fvg4h_{scenario}_{symbol}_2025"
        for scenario in ("gross", "primary", "stress")
        for symbol in SYMBOLS
    }
    assert result["candidate_possible"] is False and result["trade_authorized"] is False


def test_live_dispatch_not_stale_function(monkeypatch):
    monkeypatch.setattr(public_pilot, "fvg_screen", lambda reader, config: "replaced")
    assert public_pilot.job("public-fvg")(None, None) == "replaced"
'''
path = Path("/home/user/CryptoSyf/tests/test_fvg_integration.py")
with path.open("x") as fh:
    fh.write(integ)
print("WROTE", path, len(integ.splitlines()), "lines")

sh = await shell("cd /home/user/CryptoSyf && vis-agent python -m pytest --rootdir=/home/user/CryptoSyf -q -p no:cacheprovider tests/test_fvg_integration.py 2>&1 | tail -12", {"cwd": "/home/user/CryptoSyf"})
r = sh.wait(300)
print(r)
print(sh.logs(-14))
