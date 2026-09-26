import json, datetime

reg = {
    "schema_version": 1,
    "registered_at_utc": datetime.now(datetime.UTC).isoformat(),
    "ledger": "data/nansen-pilot.sqlite",
    "trade_authorized": False,
    "budget_consent": {
        "id": "NANSEN-BUDGET-PLUS1000-v1",
        "granted_by_user": "Session turn 21, 2026-09-09: explicit grant of 1000 additional Nansen credits.",
        "add_credits": 1000,
        "add_attempts": 600,
        "attempt_basis": "Registered pilot ratio 10 credits : 6 attempts applied to the granted amount; attempts still bind independently and never refill.",
        "caps_before": {"credit_cap": 10, "request_cap": 6},
        "caps_after": {"credit_cap": 1010, "request_cap": 606},
        "recording": "nansen-budget writes one budget_events row per unique consent reference; caps only rise, spend and blocked state persist, replayed consent is refused.",
        "public_request_cap_unchanged": 40,
    },
    "studies": [
        {
            "id": "NANSEN-FLOW-DAILY-v1",
            "parent": "S01 (frozen); daily-granularity diagnostic variant, not S01 execution",
            "stage": "G1/G2 data-availability and sign diagnostic on the historical screener",
            "claim": "Tokens with the highest positive smart-money netflow over a UTC day earn a positive equal-weight net return over the next day after the listed haircuts.",
            "entry": "Per date T among page-1 top-50 rows ordered by netflow DESC: netflow>0, volume>=100000 USD, token_age_days>=30, price_usd>0; take up to 10 by netflow, equal weight.",
            "exit": "price_usd in the snapshot of the next calendar date (approximate EOD semantics; cutoff time unverified).",
            "cost_scenarios_bps_each_side": [0, 25, 50],
            "blocking_gates_in_order": [
                "units: |netflow-(buy_volume-sell_volume)| within 1e-6 relative tolerance on every row and date, else BLOCKED_UNITS",
                "usable dates (next-date pair present and at least one entry) below 20, else BLOCKED_SHORT_SAMPLE",
                "median completable share of entries below 0.5, else BLOCKED_EXIT_DATA",
                "primary gate: median usable-date net return at 50 bps/side must exceed 0, else REJECTED (NONPOSITIVE_PRIMARY_NET)",
                "otherwise INCONCLUSIVE: single chain, page-1 universe, survivorship in completable returns, no PIT labels, no execution evidence"
            ],
            "control": "Median gross forward return of eligible rows ranked below the entries; descriptive only, never a gate.",
            "endpoint": "/api/v1beta1/token-screener/historical",
            "payload_template": payload_template := None,
            "dates": "2026-07-28..2026-08-26 daily, fetched newest-first so an early stop retains the newest evidence",
            "credit_plan": {
                "per_date": 5,
                "dates": 30,
                "cache_hits_expected": 1,
                "worst_case_new_credits": 145
            },
            "stop_rules": "Any fetch failure blocks the pilot per registered discipline; the study reports partial dates and the sanitized blocked reason. No retry, no unblock, no ledger deletion.",
            "costs_note": "Fixed, data and infrastructure costs excluded and not assumed zero; low-liquidity DEX execution expected worse than the haircut ladder.",
            "funding_policy": "CAPITAL100-v1-compatible percentage returns; each date is one separate 100-USDC scenario, never summed.",
            "trade_authorized": False
        }
    ]
}
reg["studies"][0]["payload_template"] = {
    "chains": ["solana"],
    "to_date": "<date>",
    "timeframe_days": 1,
    "trader_type": "sm",
    "exclude_sectors": ["Stablecoin"],
    "pagination": {"page": 1, "per_page": 50},
    "order_by": [{"field": "netflow", "direction": "DESC"}],
}
p = project_root_path / "research/nansen-studies.json"
p.write_text(json.dumps(reg, indent=2, ensure_ascii=True) + "\n")
print("registry written, bytes:", p.stat().st_size)
print(json.dumps(reg["studies"][0]["payload_template"]))
