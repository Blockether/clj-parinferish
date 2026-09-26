EXTRACT_BLOCK = '''            or (
                name == "public-sar"
                and body.get("audit_complete") is True
                and isinstance(body.get("archive_audit"), dict)
                and isinstance(body.get("summary"), list)
            )
            or (
                name == "public-polymarket"'''

SAR_ROWS = '''def sar_rows(artifacts):
    """Keep a blocked Parabolic SAR audit visible without inventing a result."""
    artifact = artifacts.get("public-sar") or {}
    return {
        key: artifact[key]
        for key in (
            "experiment",
            "status",
            "collection_complete",
            "archive_audit",
            "failure",
            "summary",
            "pooled",
            "sar_setup_count",
            "information_cost",
            "decision_reasons",
            "total_net_pnl_state",
            "limitations",
        )
        if key in artifact
    }


def _fvg_section(comparison):'''

SAR_SECTION = '''def _sar_section(comparison):
    result = comparison.get("sar") or {}
    lines = [
        "## 49. Parabolic SAR (klasyczny system Wildera) — przełączenie trendu — "
        + (result.get("experiment") or REGISTERED_NOT_RUN),
        "",
    ]
    if not result:
        return lines + [
            "Brak artefaktu; najpierw `public-sar`, potem `public-comparison`.",
            "",
        ]
    audit = result.get("archive_audit", {})
    verified = audit.get("verified_assets") or {}
    expected = len(audit.get("expected_months_per_asset") or [])
    lines += [
        f"Status {result.get('status')}; NO_PROMOTION / NO_TRADE.",
        f"PnL całkowity netto: {result.get('total_net_pnl_state')}; koszt danych "
        "i infrastruktury nierozliczony, USDC/USD niezweryfikowane.",
        f"Zweryfikowane miesiące na aktyw: {sorted(set(verified.values()))} z {expected}; "
        f"aktywa: {len(verified)}; błąd: "
        f"{result.get('failure') or audit.get('failure') or 'brak'}.",
        "To jedna zamrożona klasyczna interpretacja Parabolic SAR Wildera "
        "(AF 0.02/0.02/0.20, SAR kleszczowo nie idzie pod prąd trendu): dzień setupu "
        "to bycze przełączenie trendu z -1 na +1 po dotknięciu zstępującego SAR "
        "przez high dnia, wejście long na otwarciu następnego dnia, wyjście na "
        "zamknięciu pierwszego dnia, którego low dotknie wznoszącego SAR, od dnia "
        "wejścia włącznie — wynik nie waliduje klasy systemów podążających.",
        "Źródłem jest klasyczna publikacja Wildera (AF 0.02/0.02/0.20 jako "
        "opublikowane), nie odczytana strona serwisu: cap żądań publicznych "
        "wyczerpany (718/732, rezerwa 17 chroniona), więc żaden parametr serwisu "
        "nie został odczytany ani przetestowany; konwencja zasiania (pierwszy dzień "
        "otwiera trend wzrostowy, SAR = low dnia pierwszego, EP = high, AF = 0.02) "
        "i konwencja dotknięcia (low <= SAR / high >= SAR) to ARBITRARY_CONVENTION "
        "zamrożone przed uruchomieniem; siatki AF nietestowane.",
        "SAR jest systemowym wyjściem stop-and-reverse: wariant celowo bez "
        "dodatkowego stopu (ryzyko otwarte nieograniczone z konstrukcji, wyjście "
        "tylko przełączeniem albo końcem okna). Seria SAR liczona od początku "
        "archiwum 2024-12, więc zasiew przemyka przed oknem ewaluacji; wejście na "
        "otwarciu następnego dnia to konwencja rodzinna, nie klasyczne odwrócenie "
        "w cenie SAR. Ceny 2025 są już poznane: to nie jest nowy out-of-sample; "
        "jeden wariant, bez strojenia po wyniku.",
        "",
    ]
    if not result.get("collection_complete"):
        return lines + ["Wynik ekonomiczny NOT_REPORTABLE: niepełne dane całego okna.", ""]
    lines += [
        f"Dni setupu (wszystkie aktywa, także te pominięte w pozycji) w oknie: "
        f"{result.get('sar_setup_count')}.",
        "",
        "| Scenariusz | aktywa z PnL > 0 | transakcje | suma PnL USDC (opisowo) | "
        "śr. USDC/dzień/loop | opisowy CI95 średniej |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name in sorted(result.get("pooled") or {}):
        item = result["pooled"][name]
        ci = item["bootstrap_ci95_mean_daily_pnl_per_loop_usdc"]
        lines.append(
            f"| {name} | {item['assets_with_positive_net_pnl']}/{item['assets']} | "
            f"{item['closed_trades_total']} | "
            f"{_num(item['net_pnl_sum_usdc_descriptive'])} | "
            f"{_num(item['mean_daily_pnl_per_loop_usdc'], 5)} | "
            f"[{_num(ci[0], 5)}, {_num(ci[1], 5)}] |"
        )
    lines += [
        "",
        "Suma pooled jest wyłącznie opisowa: osiem niezależnych rachunków po 100 USDC, "
        "nigdy jeden wspólny rachunek ani prognoza. CI to circular block bootstrap średniego "
        "dziennego PnL na loop; korelowane aktywa i klastrowanie przełączeń trendu "
        "zaniżają zależność.",
        "",
        "| Scenariusz / aktyw | PnL USDC | % wkładu | DD USDC | DD % | transakcje | "
        "trafność % | śr. zwrot % | śr. hold h | ekspozycja % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in result.get("summary", []):
        units, risk_row = item["returns"], item["risk"]
        lines.append(
            f"| {item['label']} | {_num(units['net_pnl_usdc'])} | "
            f"{_num(units['total_return_pct'])} | "
            f"{_num(risk_row['max_drawdown_usdc'], signed=False)} | "
            f"{_num(risk_row['max_drawdown_pct_of_deposit'], digits=1, signed=False)}% | "
            f"{item['closed_trades']} | "
            f"{_num(item.get('win_rate'), digits=1, signed=False, percent=True)} | "
            f"{_num(item.get('mean_trade_net_return'), digits=3, percent=True)} | "
            f"{_num(item.get('mean_hold_hours'), digits=1, signed=False)} | "
            f"{_num(item['exposure_fraction_days'], digits=1, signed=False, percent=True)} |"
        )
    lines += [
        "",
        "Każdy wiersz to osobny, samodzielny rachunek CAPITAL100-v1; te serie celowo nie "
        "wchodzą do sekcji ryzyka i parowania (sekcja 2), bo nie są jednym ciągłym rachunkiem. "
        "Wejście market-on-open po dniu setupu i wyjście na zamknięciu dnia przełączenia "
        "to ceny referencyjne, nie fille; kolejność OHLC wewnątrz dnia nieznana, więc "
        "dotknięcie SAR liczone z pełnego zakresu dnia; bez dodatkowego stopu wariant "
        "niesie nieograniczone ryzyko śróddzienne/nocne z konstrukcji; bary dzienne "
        "z 1h; koszty w bps są założeniem.",
        "",
    ]
    return lines


def intraday_rows(artifacts):'''

r = patch(
    "/home/user/CryptoSyf/src/cryptosyf/comparison.py",
    [
        {"from": "75:bdb", "replace": '    "public-sar",\n    "public-stoch",'},
        {"from": "270:52b", "replace": EXTRACT_BLOCK},
        {"from": "3603:509", "replace": SAR_ROWS},
        {"from": "5836:569", "replace": '        "stoch": stoch_rows(comparable),\n        "sar": sar_rows(comparable),'},
        {"from": "5604:249", "replace": SAR_SECTION},
        {"from": "6480:6df", "replace": "    lines += _stoch_section(comparison)\n    lines += _sar_section(comparison)"},
    ],
)
print(r)
import ast
ast.parse(Path("/home/user/CryptoSyf/src/cryptosyf/comparison.py").read_text())
print("comparison.py ast OK")
