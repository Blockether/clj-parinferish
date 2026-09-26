import pathlib
root = pathlib.Path("/home/user/CryptoSyf")
src = (root/"src/cryptosyf/ha_study.py").read_text()

module = src.replace('"""Frozen classic Heikin-Ashi color-transition interpretation.',
'''"""Frozen classic MACD signal-cross interpretation (Appel defaults).

One preregistered variant on already-exposed hourly archives, from the
classic published MACD technique (Gerald Appel, Systems and Forecasts;
standard textbook defaults 12/26/9; the oxfordstrat catalog and any
service page were NOT fetched - the public request cap is exhausted, so
the classic publication is the only source and no service parameter was
read). A completed setup day is a bullish cross: the MACD(12,26) line on
daily closes crosses strictly above its EMA(9) signal line after being
at or below it. The loop buys at the next day's open. Exit: the close of
the first day with a bearish cross from the entry day onward (the entry
day's own cross counts). The classic signal-cross system carries no
protective stop, so the variant deliberately has none - open risk is
unbounded by construction and the window end closes any open position
at the last close. EMA seeded with the first archive close and the
signal with the first MACD value (ARBITRARY_SEED_CONVENTION frozen
before the run); the zero-line filter, histogram variants and the short
leg are out of scope: one variant, long-only, no post-result retuning.
Daily bars are complete 24-bar UTC days (nr2_study.daily_bars). Eight
standalone 100 USDC loops; the pooled panel is descriptive only.
"""'''.split('"""',2)[2].join(['"""','']) if False else None

# simpler: build the module by transforming ha_study source text
lines = src.split("\n")
# replace docstring block (first triple-quoted)
start = src.find('"""')
end = src.find('"""', start+3)
docstring = '''"""Frozen classic MACD signal-cross interpretation (Appel defaults).

One preregistered variant on already-exposed hourly archives, from the
classic published MACD technique (Gerald Appel, Systems and Forecasts;
standard textbook defaults 12/26/9; the oxfordstrat catalog and any
service page were NOT fetched - the public request cap is exhausted, so
the classic publication is the only source and no service parameter was
read). A completed setup day is a bullish cross: the MACD(12,26) line on
daily closes crosses strictly above its EMA(9) signal line after being
at or below it. The loop buys at the next day's open. Exit: the close of
the first day with a bearish cross from the entry day onward (the entry
day's own cross counts). The classic signal-cross system carries no
protective stop, so the variant deliberately has none - open risk is
unbounded by construction and the window end closes any open position
at the last close. EMA seeded with the first archive close and the
signal with the first MACD value (ARBITRARY_SEED_CONVENTION frozen
before the run); the zero-line filter, histogram variants and the short
leg are out of scope: one variant, long-only, no post-result retuning.
Daily bars are complete 24-bar UTC days (nr2_study.daily_bars). Eight
standalone 100 USDC loops; the pooled panel is descriptive only.
"""'''
body = src[end+3:]
module = docstring + body

repl = [
    ('LABEL_PREFIX = "ha1"', 'LABEL_PREFIX = "macda"'),
    ('UNSUPPORTED_HA_PROTOCOL', 'UNSUPPORTED_MACD_PROTOCOL'),
    ('REQUIRE_UTC_MIDNIGHT_BOUNDARIES', 'REQUIRE_UTC_MIDNIGHT_BOUNDARIES'),
    ('SHORT_HA_WINDOW', 'SHORT_MACD_WINDOW'),
    ('INVALID_HA_DECISION_CONFIG', 'INVALID_MACD_DECISION_CONFIG'),
    ('INVALID_HA_BOOTSTRAP_CONFIG', 'INVALID_MACD_BOOTSTRAP_CONFIG'),
    ('INSUFFICIENT_HA_COVERAGE', 'INSUFFICIENT_MACD_COVERAGE'),
    ('MISSING_HA_ARCHIVE', 'MISSING_MACD_ARCHIVE'),
    ('INCOMPLETE_HA_EVALUATION', 'INCOMPLETE_MACD_EVALUATION'),
    ('ha_setup_count', 'macd_setup_count'),
    ('"ha_red_exit"', '"bearish_cross_exit"'),
]
for a,b in repl:
    assert a in module, a
    module = module.replace(a,b)
path = root/"src/cryptosyf/macd_study.py"
path.write_text(module)
print("skeleton written (before custom fn bodies):", len(module))
